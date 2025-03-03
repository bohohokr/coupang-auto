import requests
import openai
import json
from PIL import Image, ImageDraw, ImageFont
import os

# ✅ 쿠팡 API 키 설정 (실제 키로 변경해야 함)
ACCESS_KEY = "YOUR_CUPANG_ACCESS_KEY"
SECRET_KEY = "YOUR_CUPANG_SECRET_KEY"

# ✅ GPT-3.5 API 키 설정 (실제 키로 변경해야 함)
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# ✅ 저장 폴더 생성
output_folder = "coupang_reviews"
os.makedirs(output_folder, exist_ok=True)

# ✅ 쿠팡 API에서 인기 제품 가져오기
def get_best_products():
    url = "https://api-gateway.coupang.com/v2/providers/affiliate_open_api/apis/openapi/v1/bestCategoryProducts?categoryId=0"
    headers = {
        "Authorization": f"Bearer {ACCESS_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None

# ✅ GPT-3.5로 블로그 글 생성
def generate_blog_content(product_name, product_url):
    openai.api_key = OPENAI_API_KEY
    prompt = f"""
    {product_name}의 리뷰를 작성해주세요.
    - 제품 개요
    - 디자인 및 빌드 품질
    - 성능 및 사용 경험
    - 실제 사용자 후기 분석
    - 경쟁 제품 비교
    - 추천 대상 및 구매 가이드
    - SEO 최적화된 HTML 포맷으로 작성
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000
    )
    
    blog_content = response["choices"][0]["message"]["content"]
    
    html_content = f"""
    <h1>{product_name} 리뷰 - 가성비 좋은 선택?</h1>
    <p><a href="{product_url}" target="_blank">👉 쿠팡에서 {product_name} 구매하기</a></p>
    {blog_content}
    """
    return html_content

# ✅ 제목 이미지 생성
def create_title_image(product_name):
    img_width, img_height = 800, 400
    background_color = (0, 102, 204)

    image = Image.new("RGB", (img_width, img_height), background_color)
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    text_width, text_height = draw.textsize(product_name, font=font)
    text_x = (img_width - text_width) // 2
    text_y = (img_height - text_height) // 2
    
    draw.text((text_x, text_y), product_name, fill="white", font=font)
    
    image_path = os.path.join(output_folder, f"{product_name.replace(' ', '_')}.png")
    image.save(image_path)
    return image_path

# ✅ 실행 코드
products = get_best_products()

if products:
    for product in products["data"]:
        product_name = product["productName"]
        product_url = product["productUrl"]

        # ✅ GPT-3.5로 블로그 글 생성
        blog_html = generate_blog_content(product_name, product_url)

        # ✅ HTML 파일 저장
        file_path = os.path.join(output_folder, f"{product_name.replace(' ', '_')}.html")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(blog_html)

        # ✅ 제목 이미지 생성
        create_title_image(product_name)

    print("✅ 블로그 리뷰 및 제목 이미지 생성 완료!")
else:
    print("❌ 쿠팡 API에서 제품 데이터를 가져오지 못했습니다.")
