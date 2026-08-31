import os
import json
import html
import urllib.request
from pathlib import Path

USERNAME = os.environ.get("GITHUB_USERNAME", "Henry28122025")
TOKEN = os.environ.get("GITHUB_TOKEN")

README = Path("README.md")

START_MARKER = "<!-- LANGUAGES_START -->"
END_MARKER = "<!-- LANGUAGES_END -->"

# Mapeamento de linguagens do GitHub Linguist para ícones do Devicon.
# Qualquer linguagem não listada aqui CONTINUA aparecendo, usando um ícone genérico.
ICONS = {
    "Python": "python/python-original.svg",
    "JavaScript": "javascript/javascript-original.svg",
    "TypeScript": "typescript/typescript-original.svg",
    "HTML": "html5/html5-original.svg",
    "CSS": "css3/css3-original.svg",
    "Java": "java/java-original.svg",
    "C": "c/c-original.svg",
    "C++": "cplusplus/cplusplus-original.svg",
    "C#": "csharp/csharp-original.svg",
    "PHP": "php/php-original.svg",
    "Ruby": "ruby/ruby-original.svg",
    "Go": "go/go-original-wordmark.svg",
    "Rust": "rust/rust-original.svg",
    "Kotlin": "kotlin/kotlin-original.svg",
    "Swift": "swift/swift-original.svg",
    "Dart": "dart/dart-original.svg",
    "Shell": "bash/bash-original.svg",
    "PowerShell": "powershell/powershell-original.svg",
    "Vue": "vuejs/vuejs-original.svg",
    "SCSS": "sass/sass-original.svg",
    "Sass": "sass/sass-original.svg",
    "R": "r/r-original.svg",
    "Lua": "lua/lua-original.svg",
    "Jupyter Notebook": "jupyter/jupyter-original-wordmark.svg",
    "Arduino": "arduino/arduino-original.svg",
    "Markdown": "markdown/markdown-original.svg",
    "Dockerfile": "docker/docker-original.svg",
    "React": "react/react-original.svg",
    "MATLAB": "matlab/matlab-original.svg",
    "Perl": "perl/perl-original.svg",
    "Scala": "scala/scala-original.svg",
    "Groovy": "groovy/groovy-original.svg",
    "Elixir": "elixir/elixir-original.svg",
    "Haskell": "haskell/haskell-original.svg",
    "Objective-C": "objectivec/objectivec-plain.svg",
    "Visual Basic .NET": "visualbasic/visualbasic-original.svg",
}


def github_request(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Henry28122025-Language-Stats",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    request = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def get_repositories():
    repos = []
    page = 1

    while True:
        url = (
            f"https://api.github.com/users/{USERNAME}/repos"
            f"?type=owner&sort=updated&per_page=100&page={page}"
        )

        result = github_request(url)

        if not result:
            break

        repos.extend(result)

        if len(result) < 100:
            break

        page += 1

    return repos


def get_languages():
    totals = {}

    for repo in get_repositories():
        # Não conta forks.
        if repo.get("fork"):
            continue

        # Não conta o repositório de perfil, para o README não influenciar as estatísticas.
        if repo["name"].lower() == USERNAME.lower():
            continue

        repo_name = repo["name"]
        print(f"Lendo: {repo_name}")

        url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/languages"

        try:
            languages = github_request(url)
        except Exception as error:
            print(f"Erro ao ler {repo_name}: {error}")
            continue

        for language, bytes_count in languages.items():
            totals[language] = totals.get(language, 0) + bytes_count

    return totals


def calculate_percentages(languages):
    total_bytes = sum(languages.values())

    if total_bytes == 0:
        return []

    result = []

    for language, bytes_count in languages.items():
        percentage = (bytes_count / total_bytes) * 100
        result.append((language, percentage, bytes_count))

    result.sort(key=lambda item: item[2], reverse=True)
    return result


def create_language_cell(language, percentage):
    safe_language = html.escape(language)
    icon = ICONS.get(language)

    if icon:
        icon_html = (
            '<img '
            f'src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/{icon}" '
            'width="30" height="30" '
            f'alt="{safe_language}">'
        )
    else:
        icon_html = '<span title="Linguagem detectada pelo GitHub">💻</span>'

    return (
        '<td align="center" width="95">'
        f'{icon_html}'
        '<br>'
        f'<b>{safe_language}</b>'
        '<br>'
        f'<sub>{percentage:.1f}%</sub>'
        '</td>'
    )


def generate_html(percentages):
    if not percentages:
        return "<p>No languages detected.</p>"

    languages_per_row = 6
    lines = ['<table align="center">']

    for index in range(0, len(percentages), languages_per_row):
        group = percentages[index:index + languages_per_row]
        lines.append("<tr>")

        for language, percentage, _ in group:
            lines.append(create_language_cell(language, percentage))

        lines.append("</tr>")

    lines.append("</table>")
    return "\n".join(lines)


def update_readme(generated_html):
    content = README.read_text(encoding="utf-8")

    if START_MARKER not in content:
        raise RuntimeError("LANGUAGES_START não encontrado no README.md.")

    if END_MARKER not in content:
        raise RuntimeError("LANGUAGES_END não encontrado no README.md.")

    before = content.split(START_MARKER, 1)[0]
    after = content.split(END_MARKER, 1)[1]

    new_content = (
        before
        + START_MARKER
        + "\n"
        + generated_html
        + "\n"
        + END_MARKER
        + after
    )

    README.write_text(new_content, encoding="utf-8")


def main():
    print(f"Buscando linguagens públicas de {USERNAME}...")

    languages = get_languages()
    percentages = calculate_percentages(languages)

    print("\nPorcentagens encontradas:")
    for language, percentage, _ in percentages:
        print(f"{language}: {percentage:.1f}%")

    generated_html = generate_html(percentages)
    update_readme(generated_html)

    print("\nREADME.md atualizado com sucesso!")


if __name__ == "__main__":
    main()
