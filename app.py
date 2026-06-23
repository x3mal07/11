from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

FILE_NAME = 'wishes.json'

def load_wishes():
    """Загружает желания из JSON-файла"""
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_wishes(wishes):
    """Сохраняет желания в JSON-файл"""
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(wishes, f, ensure_ascii=False, indent=2)

def get_next_id(wishes):
    """Генерирует следующий ID"""
    if not wishes:
        return 1
    return max(wish['id'] for wish in wishes) + 1

# Загружаем желания
wishes = load_wishes()

@app.route('/')
def index():
    """Главная страница со списком желаний"""
    total_price = sum(wish.get('price', 0) for wish in wishes)
    return render_template('index.html', wishes=wishes, total_price=total_price)

@app.route('/add', methods=['GET', 'POST'])
def add_wish():
    """Добавление нового желания"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', 0)
        link = request.form.get('link', '').strip()
        status = request.form.get('status', 'хочу')
        
        if not name:
            return render_template('add.html', error="Название не может быть пустым!")
        
        try:
            price = int(price)
        except ValueError:
            price = 0
        
        new_wish = {
            'id': get_next_id(wishes),
            'name': name,
            'description': description,
            'price': price,
            'link': link,
            'status': status,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        wishes.append(new_wish)
        save_wishes(wishes)
        return redirect('/')
    
    return render_template('add.html')

@app.route('/wish/<int:wish_id>')
def detail_wish(wish_id):
    """Детальный просмотр желания"""
    wish = next((w for w in wishes if w['id'] == wish_id), None)
    if wish is None:
        return "Желание не найдено", 404
    return render_template('detail.html', wish=wish)

@app.route('/edit/<int:wish_id>', methods=['GET', 'POST'])
def edit_wish(wish_id):
    """Редактирование желания"""
    wish = next((w for w in wishes if w['id'] == wish_id), None)
    if wish is None:
        return "Желание не найдено", 404
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', 0)
        link = request.form.get('link', '').strip()
        status = request.form.get('status', 'хочу')
        
        if not name:
            return render_template('edit.html', wish=wish, error="Название не может быть пустым!")
        
        try:
            price = int(price)
        except ValueError:
            price = 0
        
        wish['name'] = name
        wish['description'] = description
        wish['price'] = price
        wish['link'] = link
        wish['status'] = status
        
        save_wishes(wishes)
        return redirect('/')
    
    return render_template('edit.html', wish=wish)

@app.route('/delete/<int:wish_id>')
def delete_wish(wish_id):
    """Удаление желания"""
    global wishes
    wishes = [w for w in wishes if w['id'] != wish_id]
    save_wishes(wishes)
    return redirect('/')

@app.route('/toggle/<int:wish_id>')
def toggle_status(wish_id):
    """Переключение статуса (хочу → куплено → хочу)"""
    wish = next((w for w in wishes if w['id'] == wish_id), None)
    if wish:
        wish['status'] = 'куплено' if wish['status'] == 'хочу' else 'хочу'
        save_wishes(wishes)
    return redirect('/')

@app.route('/search')
def search():
    """Поиск по названию"""
    query = request.args.get('q', '').strip().lower()
    if query:
        filtered = [w for w in wishes if query in w['name'].lower()]
    else:
        filtered = wishes
    total_price = sum(w.get('price', 0) for w in filtered)
    return render_template('index.html', wishes=filtered, total_price=total_price, search_query=query)

@app.route('/filter/<status>')
def filter_status(status):
    """Фильтр по статусу"""
    filtered = [w for w in wishes if w.get('status') == status]
    total_price = sum(w.get('price', 0) for w in filtered)
    return render_template('index.html', wishes=filtered, total_price=total_price)

if __name__ == '__main__':
    app.run(debug=True)
