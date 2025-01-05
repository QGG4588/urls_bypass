# urls_bypass
# URL-Bypass-Scanner

一个强大的 URL Bypass 漏洞检测工具，用于自动化检测 URL 绕过漏洞。

## 功能特点

- 🚀 支持多种 URL bypass 检测模式
- 📚 内置丰富的 bypass 字典
- 🔧 支持自定义 bypass 字典
- 📝 支持批量检测多个目标
- 🔄 支持 HTTP 代理
- ⚡ 并发请求提高效率
- 🎨 彩色输出显示结果
- 💾 支持导出检测报告

## 致谢

默认字典来源于 [rainy-go/url-parsing-bypass](https://github.com/rainy-go/url-parsing-bypass)，感谢作者的贡献。

## 安装

1. 克隆仓库：

`git clone https://github.com/yourusername/url-bypass-scanner.git`

`cd url-bypass-scanner`

2. 安装依赖：
   
`pip install -r requirements.txt`

## 使用方法

### 基本用法

1. 检测单个 URL：
   
`python url_bypass_checker.py -u https://example.com/admin`

![image](https://github.com/user-attachments/assets/9ba07ede-ffbc-4a76-b244-18a521c0c3bd)


2. 批量检测 URL：

`python url_bypass_checker.py -l urls.txt`


### 高级选项

- 使用自定义字典：

`python url_bypass_checker.py -u https://example.com -d custom_bypass.txt`

- 使用代理：
  
`python url_bypass_checker.py -u https://example.com -p 127.0.0.1:8080`

- 保存检测报告：
  
`python url_bypass_checker.py -l urls.txt -o report.txt`

- 调整并发和超时：

`python url_bypass_checker.py -u https://example.com -w 20 -t 10`

### 命令行参数
-u, --url 要检查的目标 URL
-l, --list 包含多个目标 URL 的文件
-t, --timeout 请求超时时间（秒）
-w, --workers 并发工作线程数
-p, --proxy 代理服务器地址
-o, --output 检测报告输出路径
-d, --dict 自定义 bypass 字典路径



## Bypass 字典

### 内置字典类型

默认字典包含以下几类 bypass 模式：

1. URL 编码绕过
   - %09, %20, %23, %2e, %2f 等
   - %26, %3b, %3f, %40 等

2. 空字节和换行符绕过
   - %00, %0a, %0d, %0d%0a
   - ..%00/, ..%0d/

3. 目录遍历绕过
   - ../, ..\, ..%2f, ..%5c
   - .././, /.//./
   - ..;/, /..;/
   - %2e%2e%2f

4. 特殊字符绕过
   - ~, ., ;, *, @, ?
   - %2a, %26, %23, %40
   - ;%09, ;%09.., ;%2f..

5. 双斜杠绕过
   - //, \, .\, //.
   - ////, /.//./
   - \..\.\

6. 文件扩展绕过
   - .json, .css, .html, .js
   - ?.css, ?.js
   - %3f.css, %3f.js

7. 参数污染
   - /?testparam
   - /#test
   - ?a.css, ?a.js, ?a.jpg
   - /??, /???

8. 认证绕过
   - /admin/../test.log
   - ../admin
   - /admin/..;/

### 自定义字典格式

字典文件每行一个 bypass 模式，支持注释（以 # 开头）：

# URL编码绕过
%2e
%2f
目录遍历
../
..;/
特殊字符
;
# 文件扩展
.json
.css

### 字典来源

默认字典基于 [rainy-go/url-parsing-bypass](https://github.com/rainy-go/url-parsing-bypass) 项目，包含了广泛的 URL bypass 测试用例。你也可以使用 `-d` 参数指定自己的字典文件。

## 输出示例

控制台输出：

[Status: 200]

200 [Size: 1234] - https://example.com/admin%2e/index.html

200 [Size: 1240] - https://example.com/admin/..;/

200 [Size: 1156] - https://example.com/admin.json

[Status: 403]

403 [Size: 789] - https://example.com/admin/%00/index.php

403 [Size: 892] - https://example.com/admin/%2e%2e/

[Status: 404]

404 [Size: 345] - https://example.com/admin.js



## 项目结构

url-bypass-scanner/

├── url_bypass_checker.py # 主程序

├── README.md # 说明文档

├── requirements.txt # 依赖清单

└── wordlists/ # 字典目录

└── url-bypass.txt # 默认字典


## 依赖要求

- Python 3.6+
- requests
- colorama
- tqdm

## 注意事项

1. 使用代理时请确保代理服务器正常运行
2. 批量检测时建议适当调整并发数（-w 参数）
3. 对于大量目标，建议调整超时时间（-t 参数）
4. 注意目标网站的安全策略，避免触发防护机制
5. 某些 bypass 技术可能会被 WAF 拦截
6. 建议在测试时逐步增加并发数，避免对目标系统造成压力
7. 仅用于授权的安全测试，禁止非法用途

## 最佳实践

1. 先使用单个目标进行测试：

`
python url_bypass_checker.py -u https://example.com/admin -w 5 -t 3`



2. 确认无误后进行批量检测：

`python url_bypass_checker.py -l urls.txt -w 10 -t 5 -o report.txt`



3. 使用代理时先测试连接：

`python url_bypass_checker.py -u https://example.com -p 127.0.0.1:8080 -w 1`



## 常见问题

1. 连接超时
   - 检查网络连接
   - 调整超时参数
   - 减少并发数

2. 代理问题
   - 确认代理服务器状态
   - 检查代理格式是否正确

3. 结果分析
   - 关注状态码变化
   - 对比响应大小差异
   - 注意重定向情况

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 免责声明

本工具仅用于授权的安全测试，使用者需自行承担因使用不当造成的任何后果。
