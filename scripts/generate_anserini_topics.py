import json
from tqdm import tqdm
from collections import defaultdict
from argparse import ArgumentParser

def process(input_filename, output_filename):
    # 打开输入文件和输出文件
    with open(input_filename) as input_file, open(output_filename, "w+") as output_file:
        # 针对输入文件中的每一行进行迭代处理
        for inp_line in tqdm(input_file):
            # 将 JSON 格式的输入行解析为 Python 字典对象
            tmp = json.loads(inp_line)
            # 获取问题 ID
            qid = tmp["id"]
            # 将向量字典转换为字符串形式，用空格分隔键值对，并重复键值对应的值次数
            vector = " ".join([" ".join([key]*val) for key, val in tmp["vector"].items()])
            # 构建输出行，包括问题 ID 和处理后的向量
            line = f"{qid}\t{vector}\n"
            # 将处理后的行写入输出文件
            output_file.write(line)


def main():
    parser = ArgumentParser(description='Convert BLADE query vectors into an Anserini compatible query file')
    parser.add_argument('--input', dest='input', required=True)
    parser.add_argument('--output', dest='output', required=True)
    args = parser.parse_args()

    process(args.input, args.output)

if __name__ == "__main__":
    main()

