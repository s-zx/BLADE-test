#!/usr/bin/env python
import os
import re
import json
import logging
import argparse
import argparse
import os
from transformers import AutoTokenizer
from tqdm import tqdm
from typing import Dict
from transformers import AutoTokenizer


logging.getLogger("transformers.tokenization_utils_base").setLevel(logging.ERROR) 

def strip_newlines(text: str) -> str:
    text = text.replace("\n", " ")  # 用空格替换换行符
    text = re.sub("\s+", " ", text)  # 用单个空格替换连续的空白字符
    return text.lower()  # 转换文本为小写并返回

def process_documents(args) -> Dict[str, str]:
    num_docs = sum(1 for line in open(args.corpus))
    with open(args.corpus) as f:
        # 逐行读取文件中的 JSON 数据
        for line in tqdm(f, total=num_docs):
            temp = json.loads(line)  # 解析 JSON 数据
            doc_id = temp[args.docid]  # 获取文档 ID
            # 获取文档标题（如果存在的话）并去除换行符
            title = strip_newlines(temp[args.title] if args.title in temp else "")
            # 获取文档内容并去除换行符
            text = strip_newlines(temp[args.body])
            # 组合文档标题和内容，如果标题不存在，则只使用内容；再次去除换行符
            doc_text = title + " " + text if title else text
            # 使用指定的分词器对文档进行编码
            encoded_tokens = args.tokenizer.encode(doc_text)[1:-1]
            s, e, idx = 0, 0, 0
            # 将文档分割成固定长度的片段
            while s < len(encoded_tokens):
                e = s + args.length  # 计算分割片段的结束位置
                # 如果结束位置超出编码后的文档长度，则将结束位置调整为文档末尾
                if e >= len(encoded_tokens):
                    e = len(encoded_tokens)
                # 解码分割后的片段
                p = args.tokenizer.decode(encoded_tokens[s:e])
                # 生成通行证 ID，格式为“文档ID_片段序号”
                pass_id = f"{doc_id}_{idx}"
                # 计算下一个片段的起始位置
                s = s + args.length - args.stride
                # 返回解码后的片段及其对应的通行证 ID
                yield p, pass_id
                idx += 1

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Script that generates overlapping passages from a JSONL document collection")
    parser.add_argument("--root", type=str, required=True)
    parser.add_argument("--corpus", type=str, required=True)
    parser.add_argument("--model_name", type=str, required=True)
    parser.add_argument("--length", type=int, default=256)
    parser.add_argument("--stride", type=int, default=128)
    parser.add_argument("--docid", type=str, default="id")
    parser.add_argument("--title", type=str, default="title")
    parser.add_argument("--body", type=str, default="text")
    args = parser.parse_args()
    # 初始化分词器
    args.tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    # 设置输出文件路径
    pass_file = os.path.join(args.root, "collection_passages.tsv")
    map_file = os.path.join(args.root,"mapping.tsv")
    # 打开输出文件并调用生成器函数生成并写入结果
    with open(pass_file, "w") as f, open(map_file, "w") as g:
        for idx, (line1, line2) in enumerate(process_documents(args)):
            f.write(f"{idx}\t{line1}\n")  # 将片段写入 collection_passages.tsv 文件
            g.write(f"{idx}\t{line2}\n")  # 将通行证 ID 写入 mapping.tsv 文件

