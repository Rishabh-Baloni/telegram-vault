"""
Telegram Vault - Userbot Launcher
"""
import sys
from config import Config

def main():
    """
    Launch the userbot
    """
    try:
        print("👤 Starting Telegram Vault Userbot...")
        import userbot
        userbot.main()
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    print("=" * 60)
    print("      TELEGRAM VAULT - USERBOT")
    print("=" * 60)
    print()
    main()
