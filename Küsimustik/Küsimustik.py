
"""
Küsimustiku automaatprogramm (CLI)
"""

import os
import random
import unicodedata


M = 3     
N = 5      

KUSIMUSED_FILE = "kusimused_vastused.txt"
OIGED_FILE = "oiged.txt"
VALED_FILE = "valed.txt"
KOIK_FILE = "koik.txt"

SMTP_ENABLED = False   

def normalize_email(name: str) -> str:
    """Genereerib emaili kujul eesnimi.perenimi@example.com"""
    parts = name.lower().split()
    if not parts:
        return "unknown@example.com"

    def strip_accents(text):
        return ''.join(
            c for c in unicodedata.normalize("NFKD", text)
            if unicodedata.category(c) != "Mn"
        )

    first = strip_accents(parts[0])
    last = strip_accents(parts[-1]) if len(parts) > 1 else "unknown"
    return f"{first}.{last}@example.com"


def load_questions() -> dict:
    """Laeb küsimused failist kujul küsimus:vastus"""
    questions = {}

    if not os.path.exists(KUSIMUSED_FILE):
        return questions

    with open(KUSIMUSED_FILE, encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                q, a = line.strip().split(":", 1)
                questions[q] = a

    return questions


def add_question():
    print("\n--- Lisa uus küsimus ---")
    q = input("Küsimus: ").strip()
    a = input("Õige vastus: ").strip()

    if q and a:
        with open(KUSIMUSED_FILE, "a", encoding="utf-8") as f:
            f.write(f"{q}:{a}\n")
        print("Küsimus lisatud.")
    else:
        print("Küsimus või vastus oli tühi.")


def already_tested() -> set:
    """Loeb nimed failist koik.txt"""
    tested = set()

    if not os.path.exists(KOIK_FILE):
        return tested

    with open(KOIK_FILE, encoding="utf-8") as f:
        for line in f:
            name = line.split(",")[0]
            tested.add(name)

    return tested


def send_email(recipient, subject, body):
    """Simuleeritud e-kiri"""
    if not SMTP_ENABLED:
        print("\n--- SIMULEERITUD E-KIRI ---")
        print("Saaja:", recipient)
        print("Teema:", subject)
        print(body)
        print("--- LÕPP ---\n")


def run_quiz():
    questions = load_questions()

    if len(questions) < 1:
        print("Küsimusi ei leitud.")
        return

    tested = already_tested()
    session_results = []

    for i in range(M):
        print(f"\nVastaja {i+1}/{M}")
        name = input("Sisesta nimi (Enter = katkesta): ").strip()

        if not name:
            break

        if name in tested:
            print("See inimene on juba testitud.")
            continue

        email = normalize_email(name)
        selected = random.sample(list(questions.items()), min(N, len(questions)))

        correct = 0
        for idx, (q, a) in enumerate(selected, 1):
            print(f"{idx}. {q}")
            answer = input("Vastus: ").strip().lower()
            if answer == a.lower():
                correct += 1

        success = correct > len(selected) / 2
        status = "SOBIS" if success else "EI SOBINUD"

        session_results.append((name, correct, email, status))

        with open(KOIK_FILE, "a", encoding="utf-8") as f:
            f.write(f"{name},{correct},{email}\n")

        send_email(
            email,
            "Küsimustiku tulemus",
            f"Tere {name}!\n\nÕigeid vastuseid: {correct}\nStaatus: {status}"
        )

    write_results(session_results)


def write_results(results):
    """Salvestab tulemused failidesse"""
    good = [r for r in results if r[3] == "SOBIS"]
    bad = [r for r in results if r[3] == "EI SOBINUD"]

    good.sort(key=lambda x: x[1], reverse=True)
    bad.sort(key=lambda x: x[0])

    with open(OIGED_FILE, "w", encoding="utf-8") as f:
        for n, s, e, _ in good:
            f.write(f"{n} – {s} õigesti – {e}\n")

    with open(VALED_FILE, "w", encoding="utf-8") as f:
        for n, s, e, _ in bad:
            f.write(f"{n} – {s} õigesti – {e}\n")

    print("\nSessioon lõpetatud.")
    print(f"Tulemused salvestatud: {OIGED_FILE}, {VALED_FILE}, {KOIK_FILE}")




def menu():
    while True:
        print("\n--- MENÜÜ ---")
        print("1) Alusta küsimustikku")
        print("2) Lisa uus küsimus")
        print("3) Välju")

        choice = input("Valik: ").strip()

        if choice == "1":
            run_quiz()
        elif choice == "2":
            add_question()
        elif choice == "3":
            print("Programm lõpetas töö.")
            break
        else:
            print("Vale valik.")


if __name__ == "__main__":
    menu()
