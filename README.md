# Instagram Clone — Django Backend

Full-featured Instagram backend with Supabase PostgreSQL database.

## Features

| Module | Endpoints |
|--------|-----------|
| Auth | Register, Login, Logout, Token Refresh, Change Password |
| Users | Profile, Followers, Following, Suggested Users |
| Posts | CRUD, Feed, Explore, Archive, Saved, Collections, Hashtags |
| Stories | CRUD, Feed (grouped), Views, Reactions, Highlights |
| Reels | CRUD, Feed, View/Share counters |
| Comments | CRUD + nested Replies (posts & reels) |
| Likes | Like/Unlike posts, reels, comments |
| Follows | Follow, Unfollow, Block, Follow Requests (private accounts) |
| Notifications | All types, mark-read, unread count |
| Messages | DM + Group chats, reactions, read receipts, media sharing |
| Search | Users, posts, hashtags, trending |
| Upload | Supabase Storage upload endpoint |

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure .env
Copy `.env` and fill in your Supabase credentials:
```
DB_HOST=db.YOUR_PROJECT_REF.supabase.co
DB_PASSWORD=YOUR_DB_PASSWORD
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_KEY=YOUR_ANON_KEY
SUPABASE_SERVICE_KEY=YOUR_SERVICE_ROLE_KEY
```

### 3. Get your Supabase credentials
- Go to https://supabase.com → Your project → Settings → Database
- Copy **Host**, **Password**
- Go to Settings → API → copy **anon key** and **service_role key**

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Create superuser (optional)
```bash
python manage.py createsuperuser
```

### 6. Start server
```bash
python manage.py runserver
```

API будет доступен на: `http://localhost:8000/api/`

---

## API Reference

### Auth
```
POST   /api/auth/register/          — Регистрация
POST   /api/auth/login/             — Логин (email + password)
POST   /api/auth/logout/            — Логаут (нужен refresh token)
POST   /api/auth/token/refresh/     — Обновить access token
GET    /api/auth/me/                — Мой профиль
PUT    /api/auth/me/                — Обновить профиль
POST   /api/auth/me/password/       — Сменить пароль
```

### Users
```
GET    /api/users/suggested/              — Рекомендованные пользователи
GET    /api/users/{username}/            — Профиль пользователя
GET    /api/users/{username}/followers/  — Список подписчиков
GET    /api/users/{username}/following/  — Список подписок
```

### Posts
```
GET    /api/posts/feed/              — Лента (из подписок)
GET    /api/posts/explore/           — Explore
POST   /api/posts/                   — Создать пост
GET    /api/posts/{id}/              — Детали поста
PUT    /api/posts/{id}/              — Редактировать
DELETE /api/posts/{id}/              — Удалить
GET    /api/posts/user/{username}/   — Посты пользователя
GET    /api/posts/saved/             — Сохранённые посты
POST   /api/posts/{id}/save/         — Сохранить пост
DELETE /api/posts/{id}/save/         — Убрать из сохранённых
GET    /api/posts/collections/       — Мои коллекции
POST   /api/posts/collections/       — Создать коллекцию
GET    /api/posts/hashtag/{name}/    — Посты по хэштегу
GET    /api/posts/archived/          — Архив
POST   /api/posts/{id}/archive/      — Архивировать
```

### Stories
```
GET    /api/stories/feed/                      — Сторис лента
POST   /api/stories/                           — Создать сторис
GET    /api/stories/{id}/                      — Просмотр (+ авто-счётчик)
DELETE /api/stories/{id}/                      — Удалить
GET    /api/stories/{id}/viewers/              — Кто смотрел
POST   /api/stories/{id}/react/                — Реакция
GET    /api/stories/user/{username}/           — Сторисы пользователя
POST   /api/stories/highlights/                — Создать хайлайт
GET    /api/stories/highlights/user/{username}/ — Хайлайты пользователя
PUT    /api/stories/highlights/{id}/           — Редактировать хайлайт
DELETE /api/stories/highlights/{id}/           — Удалить хайлайт
```

### Reels
```
GET    /api/reels/feed/              — Лента рилсов
POST   /api/reels/                   — Загрузить рилс
GET    /api/reels/{id}/              — Детали (+ счётчик просмотров)
PUT    /api/reels/{id}/              — Редактировать
DELETE /api/reels/{id}/              — Удалить
POST   /api/reels/{id}/share/        — Поделиться (счётчик)
GET    /api/reels/user/{username}/   — Рилсы пользователя
```

### Comments
```
GET    /api/comments/post/{post_id}/   — Комментарии к посту
POST   /api/comments/post/{post_id}/   — Написать комментарий
GET    /api/comments/reel/{reel_id}/   — Комментарии к рилсу
POST   /api/comments/reel/{reel_id}/   — Написать комментарий к рилсу
PUT    /api/comments/{id}/             — Редактировать
DELETE /api/comments/{id}/             — Удалить
GET    /api/comments/{id}/replies/     — Ответы на комментарий
```

### Likes
```
POST   /api/likes/post/{id}/          — Лайкнуть пост
DELETE /api/likes/post/{id}/          — Убрать лайк
GET    /api/likes/post/{id}/likers/   — Кто лайкнул
POST   /api/likes/reel/{id}/          — Лайкнуть рилс
DELETE /api/likes/reel/{id}/          — Убрать лайк
POST   /api/likes/comment/{id}/       — Лайкнуть комментарий
DELETE /api/likes/comment/{id}/       — Убрать лайк
```

### Follows
```
POST   /api/follows/{username}/          — Подписаться
DELETE /api/follows/{username}/          — Отписаться
POST   /api/follows/{username}/accept/   — Принять запрос
DELETE /api/follows/{username}/accept/   — Отклонить запрос
DELETE /api/follows/{username}/remove/   — Удалить из подписчиков
GET    /api/follows/requests/pending/    — Входящие запросы
POST   /api/follows/block/{username}/    — Заблокировать
DELETE /api/follows/block/{username}/    — Разблокировать
GET    /api/follows/blocked/             — Список заблокированных
```

### Notifications
```
GET    /api/notifications/               — Все уведомления
GET    /api/notifications/unread/        — Количество непрочитанных
POST   /api/notifications/mark-read/     — Отметить все как прочитанные
POST   /api/notifications/{id}/mark-read/ — Отметить одно
DELETE /api/notifications/{id}/          — Удалить
```

### Messages
```
GET    /api/messages/                              — Список чатов
POST   /api/messages/                              — Новый чат/группа
GET    /api/messages/{chat_id}/                    — Детали чата
PUT    /api/messages/{chat_id}/                    — Редактировать группу
DELETE /api/messages/{chat_id}/                    — Выйти из чата
GET    /api/messages/{chat_id}/messages/           — Сообщения
POST   /api/messages/{chat_id}/messages/           — Отправить сообщение
DELETE /api/messages/{chat_id}/messages/{id}/      — Удалить сообщение
POST   /api/messages/{chat_id}/messages/{id}/react/ — Реакция
DELETE /api/messages/{chat_id}/messages/{id}/react/ — Убрать реакцию
```

### Search
```
GET    /api/search/?q={query}&type={all|users|posts|hashtags}  — Поиск
GET    /api/search/users/?q={query}   — Поиск пользователей
GET    /api/search/trending/          — Топ хэштеги
```

### Upload
```
POST   /api/upload/   — Загрузить медиа в Supabase Storage
                        Body: multipart/form-data
                        Fields: file (required), folder (optional: posts/stories/reels/avatars)
                        Returns: { url, media_type }
```

---

## Authentication

Все запросы (кроме register/login) требуют заголовок:
```
Authorization: Bearer <access_token>
```

### Пример регистрации:
```json
POST /api/auth/register/
{
  "email": "user@example.com",
  "username": "myusername",
  "full_name": "My Name",
  "password": "mypassword123",
  "password_confirm": "mypassword123"
}
```

### Пример создания поста:
```json
POST /api/posts/
{
  "caption": "My first post! #hello #instagram",
  "location": "Almaty, Kazakhstan",
  "media": [
    {
      "url": "https://...supabase.co/storage/v1/object/public/instagram-media/posts/abc.jpg",
      "media_type": "image",
      "width": 1080,
      "height": 1080,
      "order": 0
    }
  ]
}
```

## Supabase Storage Setup

1. Зайди в Supabase → Storage → Create bucket
2. Название: `instagram-media`
3. Public bucket: ✅ включи
4. Готово — файлы загружаются через `POST /api/upload/`

## Stack

- **Django 4.2** + **Django REST Framework**
- **PostgreSQL** (Supabase hosted)
- **JWT** (SimpleJWT) — access + refresh tokens
- **Supabase Storage** — медиафайлы
- **CORS** configured for React Native / web
