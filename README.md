# 🚀 UICore

<div align="center">

[![Version](https://img.shields.io/badge/version-1.1.0-purple.svg)](https://github.com/EOF-413/AmazingStreetCleaner)
[![Python](https://img.shields.io/badge/python-3.11.0-yellow.svg)](https://www.python.org/)
[![Windows](https://img.shields.io/badge/platform-Windows-blue.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

## 📋 Описание

UICore - это мощное приложение с графическим интерфейсом на PyQt5.
Приложение предоставляет удобный интерфейс для управления процессами с возможностью настройки параметров в реальном времени.

> **Примечание:** Исходный код содержит заготовку для функционала автоматического нажатия клавиш по шаблонам на экране, но в текущей версии реализован только каркас приложения.

### ✨ Возможности

- 🎨 **Современный интерфейс** - тёмная тема с анимациями на PyQt5
- ⌨️ **Глобальный хоткей** - F9 для старта/остановки
- 🔧 **Гибкие настройки** - все параметры можно менять в реальном времени
- 💾 **Сохранение настроек** - конфиг хранится в `%AppData%/EOF-413/UIC`
- 🖥️ **Кастомный заголовок** - безрамочное окно с возможностью перетаскивания
- 📌 **Поверх всех окон** - опция для фиксации окна поверх других приложений
- 🔽 **Сворачивание в трей** - работа в фоновом режиме

---

## 📦 Установка

### Запуск из исходников

```bash
# Клонирование репозитория
git clone https://github.com/EOF-413/UICore.git

# Вход в каталог
cd UICore

# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск программы
python main.py
