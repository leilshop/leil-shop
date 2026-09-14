import os
import glob
import json
import re
import urllib.request
from html.parser import HTMLParser

PROJECT_ID = 'ouygoq48'
DATASET = 'production'
TOKEN = 'skbxxq09Vg5oMFdAdfT2TxoBef72bxhsSpgZZA4dgQeitKNFAOlmd2xkvngZEn4oGJopxHzcLqR6Z4ZwIIIrrhzpbtKzLAp8LBkuIJUzYTiInqFQh6uoBehdMtXISrmR0l8H03kdOS6rRXO8iozlfhqvcRN1U3Xhcesdr9OvN9vyGaWRXXQO'

url = f'https://{PROJECT_ID}.api.sanity.io/v2021-10-21/data/mutate/{DATASET}'

exclusions = ['cart.html', 'contact.html', 'header.html', 'footer.html', 'thankyou.html', 'index.html', 'sales.html', 'admin.html']
html_files = [f for f in glob.glob('*.html') if os.path.basename(f).lower() not in exclusions]

class ProductHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_h1 = False
        self.in_slogan = False
        self.in_desc = False
        self.in_desc_container = False
        self.title = ""
        self.slogan = ""
        self.description = ""
        self.buttons = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        classes = attrs_dict.get('class', '').split()

        if tag == 'h1':
            self.in_h1 = True
        elif 'slogan' in classes:
            self.in_slogan = True
        elif 'product-desc' in classes:
            self.in_desc_container = True
        elif tag == 'p' and self.in_desc_container:
            self.in_desc = True
        elif tag == 'button' and ('size-btn' in classes or 'pinky-btn' in classes):
            self.buttons.append({
                'price': attrs_dict.get('data-price', '0'),
                'old': attrs_dict.get('data-old', ''),
                'text': ''
            })

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.in_h1 = False
        elif tag == 'p' and self.in_desc:
            self.in_desc = False
            self.in_desc_container = False

    def handle_data(self, data):
        if self.in_h1 and not self.title:
            self.title = data.strip()
        elif self.in_slogan and not self.slogan:
            self.slogan = data.strip()
            self.in_slogan = False
        elif self.in_desc:
            self.description += data
        elif self.buttons and self.buttons[-1]['text'] == '':
            self.buttons[-1]['text'] = data.strip()

mutations = []
seen_titles = set()

for file_path in html_files:
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        parser = ProductHTMLParser()
        parser.feed(content)

        title = parser.title.strip()
        if not title or title in seen_titles:
            continue

        seen_titles.add(title)

        sizes = []
        for i, btn in enumerate(parser.buttons):
            s_name = btn['text'] or f"حجم {i+1}"
            p_nums = re.findall(r'\d+', btn['price'])
            price = int(p_nums[0]) if p_nums else 0
            
            size_doc = {
                "_key": f"size_{i+1}",
                "size": s_name,
                "price": price,
                "inStock": True
            }

            if btn['old']:
                old_nums = re.findall(r'\d+', btn['old'])
                if old_nums:
                    size_doc["originalPrice"] = int(old_nums[0])

            sizes.append(size_doc)

        doc = {
            "_type": "product",
            "title": title,
            "slogan": parser.slogan.strip(),
            "description": parser.description.strip(),
            "sizes": sizes
        }

        mutations.append({"createOrReplace": doc})
        print(f"تم تجهيز: {title} ({len(sizes)} أحجام)")

    except Exception as err:
        print(f"خطأ في قراءة {file_path}: {err}")

if mutations:
    payload = json.dumps({"mutations": mutations}).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {TOKEN}'
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            print(f"\n مبروك! تم رفع {len(mutations)} منتج إلى Sanity بنجاح!")
    except urllib.error.HTTPError as e:
        print(f"\nخطأ في الطلب: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"\nخطأ عام: {e}")
else:
    print("لم يتم العثور على أي صفحات منتجات في المجلد.")