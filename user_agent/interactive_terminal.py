import os
import subprocess
import sys
from pathlib import Path

def main_menu():
    # Obtener la ruta base del proyecto
    base_path = Path(__file__).parent
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("\n🤖 MultiversX Agent Terminal\n")
        print("1. Drain Wallet")
        print("2. Swap EGLD for ASH")
        print("3. Exit")
        
        choice = input("\nSeleccione una opción (1-3): ")
        
        if choice == "1":
            reason = input("\nIngrese la razón para el drain wallet: ")
            os.environ['TRANSACTION_REASON'] = reason
            try:
                subprocess.run([sys.executable, str(base_path / "userAgent.py")])
                print("\n✅ Drain wallet ejecutado")
            except Exception as e:
                print(f"\n❌ Error: {e}")
            
        elif choice == "2":
            reason = input("\nIngrese la razón para el swap EGLD->ASH: ")
            os.environ['TRANSACTION_REASON'] = reason
            try:
                subprocess.run([sys.executable, str(base_path / "userAgentswap.py")])
                print("\n✅ Swap ejecutado")
            except Exception as e:
                print(f"\n❌ Error: {e}")
            
        elif choice == "3":
            print("\n👋 ¡Hasta luego!")
            break
            
        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main_menu() 