from flask import Flask, render_template, redirect, request, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user

app = Flask(__name__)
app.secret_key = "gizli-bir-key"

# Flask-Login ayarları
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Geçici kullanıcı veritabanı
users = {
    "kaan": {"password": "1234"},
    "admin": {"password": "admin123"}
}

# Kullanıcı sınıfı
class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    if username in users:
        return User(username)
    return None

# Oyuncu veritabanı
oyuncu_listesi = [
    "Erhan Şener", "Gülcan Şener", "Mete Yılmaz", "Şenay Yılmaz",
    "Erkan Erdoğan", "Ümit Erdoğan", "Hakan Ayanoğlu", "Kezban Ayanoğlu"
]

# Ana sayfa
@app.route('/')
@login_required
def home():
    return render_template("home.html", username=current_user.id)

# Giriş
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username]["password"] == password:
            login_user(User(username))
            return redirect(url_for('home'))
        return render_template("login.html", error="Geçersiz kullanıcı adı veya şifre.")
    return render_template("login.html")

# Kayıt
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users:
            return render_template("signup.html", error="Bu kullanıcı adı zaten kayıtlı.")
        users[username] = {"password": password}
        login_user(User(username))
        return redirect(url_for('home'))
    return render_template("signup.html")

# Çıkış
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Yeni oyun başlatma – oyuncu seçimi
@app.route('/new_game', methods=['GET', 'POST'])
@login_required
def new_game():
    if request.method == 'POST':
        secilen = request.form.getlist('secili_oyuncular')
        if len(secilen) != 4:
            return render_template("new_game.html", oyuncular=oyuncu_listesi, error="Lütfen tam 4 oyuncu seçin.")
        session['players'] = secilen
        session['scores'] = [0, 0, 0, 0]
        session['history'] = []
        return redirect(url_for('yazboz'))

    return render_template("new_game.html", oyuncular=oyuncu_listesi)

# Yazboz sayfası
@app.route('/yazboz')
@login_required
def yazboz():
    if 'players' not in session:
        return redirect(url_for('new_game'))
    return render_template(
        'yazboz.html',
        players=session['players'],
        scores=session['scores'],
        history=session['history']
    )

# Puan ekleme
@app.route('/add_scores', methods=['POST'])
@login_required
def add_scores():
    try:
        yeni_puanlar = []
        for i in range(len(session['players'])):
            yeni = int(request.form.get(f'puan{i}', 0))
            yeni_puanlar.append(yeni)

        # Güncel puanlara ekle
        session['scores'] = [eski + yeni for eski, yeni in zip(session['scores'], yeni_puanlar)]
        session['history'].append(yeni_puanlar)
        return redirect(url_for('yazboz'))
    except Exception as e:
        return f"Bir hata oluştu: {e}", 400

# Oyunu sıfırla
@app.route('/reset_game')
@login_required
def reset_game():
    session.pop('players', None)
    session.pop('scores', None)
    session.pop('history', None)
    return redirect(url_for('new_game'))

if __name__ == '__main__':
    app.run(debug=True)
