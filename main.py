import train

if __name__ == "__main__":
    env_config = {
        "PYTESSERACT_PATH": r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        "MONITOR": 2,
        "DEBUG_MODE": False,
        "GAME_MODE": "PVP",
        "PLAYER_HP": 1900,
        "PLAYER_STAMINA": 150,
    }

    CREATE_NEW_MODEL = True

    print("Model started")
    train.train(CREATE_NEW_MODEL, env_config)