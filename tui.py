import curses
import os
from engine import search_pipeline

def draw_menu(stdscr):
    # PATH
    GENOMES_PATH = os.getenv("GENOMES_PATH", "./genomes")
    
    curses.curs_set(1)
    stdscr.clear()
    sh, sw = stdscr.getmaxyx()

    stdscr.addstr(1, 2, f"RASP-BLAST TUI | Path: {GENOMES_PATH}", curses.A_BOLD)
    stdscr.addstr(2, 2, "-" * (sw-4))

    stdscr.addstr(4, 2, "Inserisci sequenza DNA e premi INVIO:")
    curses.echo()
    query = stdscr.getstr(5, 2, 60).decode("utf-8")
    curses.noecho()

    if not query:
        return

    stdscr.addstr(7, 2, "[*] Elaborazione in corso sui core del Raspberry...", curses.A_DIM)
    stdscr.refresh()

    try:
        results = search_pipeline(query, GENOMES_PATH)

        # Visualizzazione Risultati
        stdscr.addstr(9, 2, f"{'FILE':<15} | {'SCORE':<6} | {'HEADER':<20}", curses.A_UNDERLINE)
        for i, res in enumerate(results[:sh-12]): # Limita i risultati all'altezza dello schermo
            line = f"{res['file']:<15} | {res['score']:<6} | {res['header']:<20}"
            stdscr.addstr(10 + i, 2, line)

        if not results:
            stdscr.addstr(10, 2, "Nessun match trovato.")

    except Exception as e:
        stdscr.addstr(9, 2, f"Errore: {str(e)}", curses.color_pair(1))

    stdscr.addstr(sh-2, 2, "Premi un tasto per uscire...")
    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    path = os.getenv("GENOMES_PATH", "./genomes")
    if not os.path.exists(path):
        os.makedirs(path)
        
    curses.wrapper(draw_menu)
