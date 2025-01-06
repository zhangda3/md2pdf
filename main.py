import pdfkit
import pypandoc
import os
from bs4 import BeautifulSoup
import requests


def get_file_name(file_list, outlist):
    print('【当前目录】Markdown文件如下：')
    for each in os.listdir():
        if ".md" in each:
            file_list.append(each)
            print(each)
            filename = each.replace('.md', '.pdf')
            outlist.append(filename)
    print('检索完毕')


def remove_unreachable_resources(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # 移除无法访问的 <img> 标签
    for img in soup.find_all('img'):
        if 'src' in img.attrs:
            try:
                response = requests.head(img['src'], timeout=2)
                if response.status_code >= 400:
                    img.decompose()  # 移除无法访问的标签
            except requests.RequestException:
                img.decompose()  # 移除无法访问的标签

    # 移除无法访问的 <link> 标签（通常是 CSS）
    for link in soup.find_all('link'):
        if 'href' in link.attrs:
            try:
                response = requests.head(link['href'], timeout=2)
                if response.status_code >= 400:
                    link.decompose()  # 移除无法访问的标签
            except requests.RequestException:
                link.decompose()  # 移除无法访问的标签

    # 移除无法访问的 <script> 标签
    for script in soup.find_all('script'):
        if 'src' in script.attrs:
            try:
                response = requests.head(script['src'], timeout=2)
                if response.status_code >= 400:
                    script.decompose()  # 移除无法访问的标签
            except requests.RequestException:
                script.decompose()  # 移除无法访问的标签

    return str(soup)


def convert(input, output):
    # 将 Markdown 文件转换为 HTML
    pypandoc.convert_file(input, 'html', outputfile='tmp.html')

    # 读取并拼接 HTML 头部和尾部
    with open("html_head.txt", "r", encoding='utf-8') as html_head_file:
        html_head = html_head_file.read()
    with open('tmp.html', "r", encoding='utf-8') as html_body_file:
        html_body_txt = html_body_file.read()
    html_body = html_head + html_body_txt + "\n</body>\n</html>"

    # 移除无法访问的资源
    cleaned_html = remove_unreachable_resources(html_body)

    # 写入最终的 HTML 文件
    with open('tmp.html', 'w', encoding='utf-8') as f:
        f.write(cleaned_html)

    # 配置 wkhtmltopdf 的路径（如果需要）
    configuration = None
    wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # 替换成您自己的路径
    if os.path.exists(wkhtmltopdf_path):
        configuration = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    # 设置 PDFKit 选项
    options = {
        "enable-local-file-access": None,
        "load-error-handling": "ignore",  # 忽略加载错误
        "javascript-delay": "2000",  # 延迟2秒以确保JavaScript执行完成
        "no-stop-slow-scripts": None,  # 不因慢脚本而停止
        "disable-smart-shrinking": None,  # 禁用智能缩小，有时可以解决一些布局问题
        "quiet": None,  # 减少输出信息
        "disable-external-links": None,  # 禁用外部链接
        "disable-internal-links": None,  # 禁用内部链接
        "disable-javascript": None  # 禁用JavaScript
    }

    # 使用 PDFKit 生成 PDF
    try:
        pdfkit.from_file('tmp.html', output, configuration=configuration, options=options, verbose=True)
    except Exception as e:
        print(f"转换 {input} 时出错: {e}")
        if os.path.exists('tmp.html'):
            os.remove('tmp.html')
        return

    # 清理临时文件
    if os.path.exists('tmp.html'):
        os.remove('tmp.html')

    print(f"{input} 转换成功！")


# 获取文件名列表
filelist = []
otfilename = []
get_file_name(filelist, otfilename)

# 批量转换
for i in range(len(filelist)):
    convert(filelist[i], otfilename[i])
