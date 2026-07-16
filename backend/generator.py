import secrets
import string
import random

class PasswordGenerator:
    """
    Quantum-inspired Password Generator Engine.
    Provides cryptographically secure random passwords and smart keyword-based strings.
    """

    @staticmethod
    def generate_random(length: int = 16, use_uppercase=True, use_numbers=True, use_symbols=True) -> str:
        """
        Produce a high-entropy random password using secrets module.
        """
        chars = string.ascii_lowercase
        if use_uppercase: chars += string.ascii_uppercase
        if use_numbers: chars += string.digits
        if use_symbols: chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if length < 4: length = 4 # Sanity check

        # Ensure at least one of each requested type is present
        pwd = []
        if use_uppercase: pwd.append(secrets.choice(string.ascii_uppercase))
        if use_numbers: pwd.append(secrets.choice(string.digits))
        if use_symbols: pwd.append(secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))
        
        while len(pwd) < length:
            pwd.append(secrets.choice(chars))
        
        random.shuffle(pwd)
        return "".join(pwd)

    @staticmethod
    def generate_smart(keyword: str, length: int = 16) -> str:
        """
        Generate a secure but memorable password based on a keyword.
        Uses leet-speak substitutions and random padding.
        """
        subs = {
            'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$', 't': '7'
        }
        
        # 1. Transform keyword
        smart_base = "".join([subs.get(c.lower(), c) for c in keyword])
        if len(smart_base) > 0:
            smart_base = smart_base[0].upper() + smart_base[1:]
        
        # 2. Add padding to reach target length
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        while len(smart_base) < length:
            smart_base += secrets.choice(alphabet)
            
        return smart_base

if __name__ == "__main__":
    # Test Suite
    print("🚀 Testing Password Generator...")
    
    rand_pwd = PasswordGenerator.generate_random(12)
    print(f"🔹 Random: {rand_pwd}")
    assert len(rand_pwd) == 12
    
    smart_pwd = PasswordGenerator.generate_smart("Nebula", 16)
    print(f"🔹 Smart (Nebula): {smart_pwd}")
    assert smart_pwd.startswith("N3bul@")
    
    print("\n✨ STAGE 13 GENERATOR TEST PASSED!")
