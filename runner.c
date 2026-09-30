#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <libgen.h>
#include <signal.h>
#include <sys/wait.h>
#include <sys/stat.h>

int main(int argc, char *argv[]) {
    // Determine the directory where this ELF runner is located
    char exe_dir[1024];
    ssize_t len = readlink("/proc/self/exe", exe_dir, sizeof(exe_dir) - 1);
    if (len != -1) {
        exe_dir[len] = '\0';
        char *dir = dirname(exe_dir);
        if (chdir(dir) != 0) {
            perror("chdir failed");
        }
    }

    // Ensure history and screenshots folders exist
    mkdir(".undo_history", 0755);
    mkdir("laporan_screenshots", 0755);

    // Handle CLI shortcuts directly: --undo, --redo, --truth-table, --batch-capture, --equation, --snapshot
    if (argc > 1) {
        if (strcmp(argv[1], "--help") == 0 || strcmp(argv[1], "-h") == 0) {
            printf("Digital Works 3.0 Modded CLI Runner\n");
            printf("Usage: ./digitalworks [OPTIONS] [FILE.dwm]\n\n");
            printf("Options:\n");
            printf("  --ai [prompt]        Generate circuit using Gemini AI Agent\n");
            printf("  --set-key [key]      Set Gemini API key\n");
            printf("  --grid               Toggle Word Layout Grid overlay\n");
            printf("  --grid-info          Display current grid slots and occupancy\n");
            printf("  --truth-table        Generate accurate real truth table from active circuit\n");
            printf("  --export-tsv         Export truth table as TSV (ready for Word paste)\n");
            printf("  --export-latex       Export truth table as LaTeX code\n");
            printf("  --equation           Generate boolean algebraic equation (f(A,B))\n");
            printf("  --batch-screens      Capture batch state screenshots for lab report\n");
            printf("  --undo               Undo last canvas operation\n");
            printf("  --redo               Redo last canvas operation\n");
            printf("  --snapshot           Take manual snapshot of current circuit\n");
            printf("  --help, -h           Show this help message\n");
            return 0;
        }
        if (strcmp(argv[1], "--export-tsv") == 0) {
            execlp("python3", "python3", "dw_undo_engine.py", "--export-tsv", NULL);
            return 0;
        }
        if (strcmp(argv[1], "--export-latex") == 0) {
            execlp("python3", "python3", "dw_undo_engine.py", "--export-latex", NULL);
            return 0;
        }
        if (strcmp(argv[1], "--batch-screens") == 0 || strcmp(argv[1], "--batch-capture") == 0 || strcmp(argv[1], "-bc") == 0) {
            execlp("python3", "python3", "dw_undo_engine.py", "--batch-screens", NULL);
            return 0;
        }
        if (strcmp(argv[1], "--undo") == 0 || strcmp(argv[1], "-u") == 0) {
            execlp("python3", "python3", "dw_undo_engine.py", "--undo", NULL);
            return 0;
        }
        if (strcmp(argv[1], "--redo") == 0 || strcmp(argv[1], "-r") == 0) {
            execlp("python3", "python3", "dw_undo_engine.py", "--redo", NULL);
            return 0;
        }
        if (strcmp(argv[1], "--truth-table") == 0 || strcmp(argv[1], "-tt") == 0) {
            execlp("python3", "python3", "dw_undo_engine.py", "--truth-table", NULL);
            return 0;
        }
        if (strcmp(argv[1], "--equation") == 0 || strcmp(argv[1], "-eq") == 0) {
            execlp("python3", "python3", "dw_undo_engine.py", "--equation", NULL);
            return 0;
        }
        if (strcmp(argv[1], "--grid") == 0 || strcmp(argv[1], "-g") == 0) {
            execlp("python3", "python3", "dw_undo_engine.py", "--grid", NULL);
            return 0;
        }
        if (strcmp(argv[1], "--grid-info") == 0) {
            execlp("python3", "python3", "dw_undo_engine.py", "--grid-info", NULL);
            return 0;
        }
        if (strcmp(argv[1], "--snapshot") == 0 || strcmp(argv[1], "-s") == 0) {
            execlp("python3", "python3", "dw_undo_engine.py", "--snapshot", NULL);
            return 0;
        }
        if (strcmp(argv[1], "--ai") == 0 || strcmp(argv[1], "-ai") == 0) {
            char *py_argv[argc + 2];
            py_argv[0] = "python3";
            py_argv[1] = "dw_undo_engine.py";
            for (int i = 1; i < argc; i++) {
                py_argv[i + 1] = argv[i];
            }
            py_argv[argc + 1] = NULL;
            execvp("python3", py_argv);
            return 0;
        }
        if (strcmp(argv[1], "--set-key") == 0) {
            char *py_argv[argc + 2];
            py_argv[0] = "python3";
            py_argv[1] = "dw_undo_engine.py";
            for (int i = 1; i < argc; i++) {
                py_argv[i + 1] = argv[i];
            }
            py_argv[argc + 1] = NULL;
            execvp("python3", py_argv);
            return 0;
        }
    }

    // Set clean native environment variables
    setenv("WINE_DISABLE_WINEBOOT", "1", 0);
    setenv("WINEDEBUG", "-all", 1);
    setenv("GDK_BACKEND", "x11", 0);

    // Ensure Caelestia Matcha Theme is registered in Wine prefix
    if (access("caelestia_theme.reg", R_OK) == 0) {
        system("wine regedit /S caelestia_theme.reg 2>/dev/null &");
    }

    // Spawn the background Sentinel Engine (Silent mode, 0 external GUI)
    pid_t sentinel_pid = fork();
    if (sentinel_pid == 0) {
        execlp("python3", "python3", "dw_undo_engine.py", NULL);
        _exit(1);
    }

    // Spawn DigitalWorks.exe (which now has the "Mods" menu embedded in its UI header)
    pid_t app_pid = fork();
    if (app_pid == 0) {
        char *new_argv[argc + 2];
        new_argv[0] = "./DigitalWorks.exe";
        for (int i = 1; i < argc; i++) {
            new_argv[i] = argv[i];
        }
        new_argv[argc] = NULL;

        execv("./DigitalWorks.exe", new_argv);

        // Fallback to wine
        char *wine_argv[argc + 3];
        wine_argv[0] = "wine";
        wine_argv[1] = "./DigitalWorks.exe";
        for (int i = 1; i < argc; i++) {
            wine_argv[i + 1] = argv[i];
        }
        wine_argv[argc + 1] = NULL;
        execvp("wine", wine_argv);

        perror("Gagal menjalankan DigitalWorks");
        _exit(1);
    }

    // Wait for DigitalWorks.exe to finish
    int status;
    waitpid(app_pid, &status, 0);

    // Clean up background sentinel
    if (sentinel_pid > 0) {
        kill(sentinel_pid, SIGTERM);
        waitpid(sentinel_pid, NULL, 0);
    }

    return 0;
}
