import os

from tests.benchmarks.common.downloads import download_if_missing


FILES = {
    "100k": [
        "guiling_chen_11ccc069-2a93-4e9d-af03-cdacb0b8d568_benchmark_en.json",
        "linchuan_shen_600bfee5-c87e-4fa9-ba36-14f9777bff6d_benchmark_en.json",
        "yu_zhou_9fdf4fb7-c6d8-4fb1-9e01-581d5b85d84a_benchmark_en.json",
    ],
    "500k": [
        "hao_lin_5857744e-07fc-4db3-a86f-46b1b956641b_benchmark_en.json",
        "jianguo_li_157c536e-cf63-4b96-acde-13a668618023_benchmark_en.json",
        "minghui_li_2289bf34-6dcb-457f-bdff-3f4f0894130d_benchmark_en.json",
        "xiaoyu_lin_2684282b-1e09-42a8-9425-533e2a95901d_benchmark_en.json",
        "xiaoyu_lin_d4f00c57-092e-4748-bc51-bdd4c84ec31f_benchmark_en.json",
        "xiaoyun_lin_b99ae361-6c8d-4815-8b53-42e0f637bf63_benchmark_en.json",
        "ziang_lin_b2df4690-4d0e-47f3-b863-f8584bd5880c_benchmark_en.json",
    ],
}


def download_clonemem_data():
    base_url = "https://huggingface.co/datasets/ZhiyuZhangA/CloneMem/resolve/main"
    target_dir = "tests/benchmarks/clonemem/data"
    for context_len, files in FILES.items():
        for file_name in files:
            download_if_missing(
                f"{base_url}/{context_len}/{file_name}?download=true",
                os.path.join(target_dir, context_len, file_name),
            )


if __name__ == "__main__":
    download_clonemem_data()
