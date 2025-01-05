#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.parse
import requests
from colorama import init, Fore
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
import argparse
import sys
from pathlib import Path

# 初始化 colorama
init(autoreset=True)


class URLBypassChecker:
    def __init__(self, timeout=5, max_workers=10, proxy=None):
        self.timeout = timeout
        self.max_workers = max_workers
        self.proxy = self._format_proxy(proxy) if proxy else None
        self.default_bypass_file = Path(__file__).parent / "url-bypass.txt"

    def _format_proxy(self, proxy):
        """格式化代理地址"""
        if not proxy.startswith(('http://', 'https://')):
            proxy = f'http://{proxy}'
        return {
            'http': proxy,
            'https': proxy
        }

    def load_bypass_patterns(self, bypass_file=None):
        """加载 URL bypass 字典"""
        try:
            file_path = bypass_file or self.default_bypass_file
            with open(file_path, 'r', encoding='utf-8') as f:
                patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            return patterns
        except FileNotFoundError:
            print(f"{Fore.RED}错误: Bypass字典文件 '{file_path}' 未找到")
            print(f"{Fore.YELLOW}使用默认测试模式: ['.html']")
            return ['.html']

    def generate_bypass_urls(self, base_url, patterns):
        """生成所有可能的 bypass URL 组合"""
        urls = set()
        parsed_url = urllib.parse.urlparse(base_url)
        base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        initial_path = parsed_url.path.strip('/')

        for pattern in patterns:
            if initial_path:
                path_parts = [p for p in initial_path.split('/') if p]
            else:
                path_parts = []

            # 在每个路径段后添加 bypass 模式
            for i in range(len(path_parts) + 1):
                current_parts = path_parts[:i] + [pattern] + path_parts[i:]
                url = urllib.parse.urljoin(
                    base_domain + '/',
                    '/'.join(filter(None, current_parts))
                )
                urls.add(url)

        return list(urls)

    def check_single_url(self, url):
        """检查单个 URL 的状态"""
        try:
            response = requests.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                proxies=self.proxy
            )
            status_code = response.status_code
            content_length = len(response.content)
            return {
                'url': url,
                'status': status_code,
                'length': content_length,
                'success': True,
                'message': f"{status_code} [Size: {content_length}]"
            }
        except requests.RequestException as e:
            return {
                'url': url,
                'status': None,
                'length': 0,
                'success': False,
                'message': str(e)
            }

    def check_urls_from_list(self, urls_file, patterns, output_file=None):
        """从文件读取 URL 列表并检查"""
        try:
            with open(urls_file, 'r') as f:
                base_urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"{Fore.RED}错误: URL列表文件 '{urls_file}' 未找到")
            sys.exit(1)

        all_results = []
        for base_url in base_urls:
            urls = self.generate_bypass_urls(base_url, patterns)
            results = self.check_urls(urls)
            all_results.extend(results)

        if output_file:
            self.save_results(all_results, output_file)

        return all_results

    def check_urls(self, urls):
        """并发检查所有 URL"""
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.check_single_url, url): url for url in urls}

            with tqdm(total=len(urls), desc="检查 URL") as pbar:
                for future in as_completed(future_to_url):
                    result = future.result()
                    results.append(result)
                    pbar.update(1)

        return results

    def save_results(self, results, output_file):
        """保存结果到文件"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("URL Bypass 检测报告\n")
                f.write("=" * 50 + "\n\n")

                # 按状态码分组
                status_groups = {}
                for result in results:
                    status = result['status'] if result['success'] else 'ERROR'
                    if status not in status_groups:
                        status_groups[status] = []
                    status_groups[status].append(result)

                # 写入分组结果
                for status in sorted(status_groups.keys()):
                    f.write(f"\n[Status: {status}]\n")
                    for result in status_groups[status]:
                        f.write(f"{result['message']} - {result['url']}\n")

                f.write(f"\n总计检查URL数: {len(results)}\n")
                f.write(f"检测时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        except Exception as e:
            print(f"{Fore.RED}保存结果到文件时出错: {e}")

    def display_results(self, results):
        """格式化显示结果"""
        # 按状态码分组显示结果
        status_groups = {}
        for result in results:
            status = result['status'] if result['success'] else 'ERROR'
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(result)

        # 分别处理错误和正常状态码
        # 首先显示错误信息
        if 'ERROR' in status_groups:
            print("\n[Status: ERROR]")
            for result in status_groups['ERROR']:
                print(f"{Fore.RED}{result['message']} - {result['url']}")
            del status_groups['ERROR']

        # 然后显示正常的状态码（数字）
        for status in sorted(status_groups.keys(), key=lambda x: int(x) if x != 'ERROR' else -1):
            print(f"\n[Status: {status}]")
            for result in status_groups[status]:
                if result['success']:
                    if result['status'] == 200:
                        color = Fore.GREEN
                    elif 400 <= result['status'] < 500:
                        color = Fore.YELLOW
                    elif result['status'] >= 500:
                        color = Fore.RED
                    else:
                        color = Fore.BLUE
                else:
                    color = Fore.RED

                print(f"{color}{result['message']} - {result['url']}")


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='URL Bypass 检测工具 - 用于检测URL绕过漏洞',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', '--url', help='要检查的基础 URL')
    group.add_argument('-l', '--list', help='包含URL列表的文件路径')

    parser.add_argument('-t', '--timeout', type=int, default=5,
                        help='请求超时时间（秒），默认为5秒')
    parser.add_argument('-w', '--workers', type=int, default=10,
                        help='并发工作线程数，默认为10')
    parser.add_argument('-p', '--proxy', help='代理服务器地址 (例如: 127.0.0.1:8080)')
    parser.add_argument('-o', '--output', help='输出结果到指定文件')
    parser.add_argument('-d', '--dict', help='自定义 bypass 字典文件路径')
    return parser.parse_args()


def main():
    args = parse_arguments()

    # 创建检查器实例
    checker = URLBypassChecker(
        timeout=args.timeout,
        max_workers=args.workers,
        proxy=args.proxy
    )

    # 加载 bypass 模式
    bypass_patterns = checker.load_bypass_patterns(args.dict)

    # 打印启动信息
    print("\nURL Bypass 检测工具启动")
    print("=" * 50)
    print(f"配置信息:")
    print(f"- 超时设置: {args.timeout}秒")
    print(f"- 并发数量: {args.workers}")
    print(f"- 代理设置: {args.proxy if args.proxy else '未使用'}")
    print(f"- 字典文件: {args.dict if args.dict else '默认字典'}")
    print(f"- 输出文件: {args.output if args.output else '仅控制台输出'}")
    print(f"- 加载规则: {len(bypass_patterns)} 条")
    print("=" * 50 + "\n")

    start_time = time.time()

    # 根据输入方式选择处理方法
    if args.url:
        urls = checker.generate_bypass_urls(args.url, bypass_patterns)
        results = checker.check_urls(urls)
        if args.output:
            checker.save_results(results, args.output)
    else:
        results = checker.check_urls_from_list(args.list, bypass_patterns, args.output)

    # 显示结果
    print("\n检测结果:")
    checker.display_results(results)

    end_time = time.time()
    print(f"\n总计用时: {end_time - start_time:.2f} 秒")
    print(f"检测URL数: {len(results)}")


if __name__ == "__main__":
    main()
