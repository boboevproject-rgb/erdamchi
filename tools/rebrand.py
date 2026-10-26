"""Filee -> Erdamchi rebrand of the forked source tree. usage: python -X utf8 -I rebrand.py <repo_root>"""
import re, sys, json, uuid, pathlib, collections
ROOT = pathlib.Path(sys.argv[1])
NEW, NEWL = "Erdamchi", "erdamchi"
REPO = "https://github.com/boboevproject-rgb/erdamchi"
GH = "boboevproject-rgb"; AUTHOR = "Bilol Bobozoda"; EMAIL = "boboevproject@gmail.com"
rep = collections.Counter()

EXCLUDE = re.compile(r"Filee\.[A-Z]|FileeExplorerMenu|Filee\.ExplorerMenu|CN=Filee|FileeRelease|FileeRepositoryUrl|FileeSetupPublish|FileeNativeWayland|FILEE_|Filee\.slnx|Filee\.iss")


def brand(text):
    """Brand replacement inside one literal/value: links first, then the word unless it is an internal identifier."""
    t = text.replace("github.com/KnifeLemon/Filee", f"github.com/{GH}/{NEWL}").replace("KnifeLemon", GH)
    t = t.replace("https://filee.sh/", REPO + "/").replace("filee.sh", f"github.com/{GH}/{NEWL}")
    t = t.replace("Filee.exe", NEW + ".exe").replace("filee-cli", NEWL + "-cli").replace("filee.cmd", NEWL + ".cmd")
    if EXCLUDE.search(t):
        return t
    t = t.replace("Filee", NEW)
    t = re.sub(r"\bfilee\b(?![-.])", NEWL, t)   # the "filee" command in help texts
    return t


def write(p, s, old):
    if s != old:
        p.write_text(s, encoding="utf-8", newline="")
        rep[str(p.relative_to(ROOT))] += 1


# ---- 1. MSBuild metadata
p = ROOT / "Directory.Build.props"; s = o = p.read_text(encoding="utf-8")
s = s.replace("<Product>Filee</Product>", f"<Product>{NEW}</Product>")
s = s.replace("<Authors>Filee contributors</Authors>", f"<Authors>{AUTHOR}, Filee contributors</Authors>")
s = s.replace("<Copyright>Copyright (c) Filee contributors</Copyright>",
              f"<Copyright>Copyright (c) 2026 {AUTHOR}. Based on Filee, Copyright (c) Filee contributors (MIT)</Copyright>")
s = s.replace("<FileeRepositoryUrl>https://github.com/KnifeLemon/Filee</FileeRepositoryUrl>", f"<FileeRepositoryUrl>{REPO}</FileeRepositoryUrl>")
write(p, s, o)
for rel, a, b in [("src/Filee.App/Filee.App.csproj", "<AssemblyName>Filee</AssemblyName>", f"<AssemblyName>{NEW}</AssemblyName>"),
                  ("src/Filee.Cli/Filee.Cli.csproj", "<AssemblyName>filee-cli</AssemblyName>", f"<AssemblyName>{NEWL}-cli</AssemblyName>")]:
    p = ROOT / rel; s = o = p.read_text(encoding="utf-8"); assert a in s, rel; write(p, s.replace(a, b), o)

# ---- 2. C# string literals (src only, not tests)
LIT = re.compile(r'\$?"""[\s\S]*?"""|(?:\$@|@\$|@)"(?:[^"]|"")*"|\$?"(?:\\.|[^"\\\n])*"')
for p in sorted((ROOT / "src").rglob("*.cs")):
    s = o = p.read_text(encoding="utf-8")
    s = LIT.sub(lambda m: brand(m.group(0)), s)
    write(p, s, o)
# setup identity that must not collide with the installed Filee
p = ROOT / "src/Filee.Setup/Installation/SetupNames.cs"; s = o = p.read_text(encoding="utf-8")
s = s.replace('AppGuid = "C8686E06-8327-40A2-B0F7-3DEDD61D9248"', f'AppGuid = "{str(uuid.uuid4()).upper()}"')
s = s.replace('Publisher = "Filee contributors"', f'Publisher = "{AUTHOR}"'); write(p, s, o)
p = ROOT / "src/Filee.Platform.Windows/ExplorerMenuPackage.cs"; s = o = p.read_text(encoding="utf-8")
s = s.replace('"PublisherDisplayName", "Filee contributors"', f'"PublisherDisplayName", "{AUTHOR}"'); write(p, s, o)
# sponsors: only the owner's GitHub
p = ROOT / "src/Filee.App/Services/SponsorLinks.cs"; s = o = p.read_text(encoding="utf-8")
s = re.sub(r'GitHubSponsorsUrl = "[^"]+"', f'GitHubSponsorsUrl = "https://github.com/{GH}"', s)
for name in ("FairyUrl", "PatreonUrl", "KoFiUrl", "PayPalUrl"):
    s = re.sub(name + r' = "[^"]+"', f'{name} = "https://github.com/{GH}"', s)
s = re.sub(r'public static IReadOnlyList<SponsorLink> For\(string language\) => language == "ko"\s*\?\s*\[[^\]]*\]\s*:\s*\[[^\]]*\];',
           'public static IReadOnlyList<SponsorLink> For(string language) => [GitHub];', s)
assert "=> [GitHub];" in s; write(p, s, o)

# ---- 3. AXAML attribute values and text nodes
for p in sorted((ROOT / "src").rglob("*.axaml")):
    s = o = p.read_text(encoding="utf-8")
    s = re.sub(r'="([^"]*Filee[^"]*)"',
               lambda m: '="' + (m.group(1) if re.search(r"using:|clr-namespace:|x:Class|Filee\.[A-Z]", m.group(0)) else brand(m.group(1))) + '"', s)
    s = re.sub(r'>([^<]*\bFilee\b[^<]*)<', lambda m: ">" + brand(m.group(1)) + "<", s)
    write(p, s, o)

# ---- 4. app manifests, Explorer menu C sources
for p in list(ROOT.rglob("app.manifest")) + [ROOT / "src/Filee.ExplorerMenu/FileeExplorerMenu.c", ROOT / "src/Filee.ExplorerMenu/FileeExplorerMenu.rc"]:
    if "tests" in p.parts or not p.exists():
        continue
    s = o = p.read_text(encoding="utf-8", errors="surrogateescape")
    s = LIT.sub(lambda m: brand(m.group(0)), s)            # C string literals / XML attribute values
    s = s.replace('L"Convert with Filee"', f'L"Convert with {NEW}"').replace('L"Filee\\\\explorer-menu.txt"', f'L"{NEW}\\\\explorer-menu.txt"')
    s = s.replace('L"Filee.exe"', f'L"{NEW}.exe"').replace('L"Filee-convert-"', f'L"{NEW}-convert-"')
    s = s.replace('"Filee contributors"', f'"{AUTHOR}"').replace('Copyright (c) Filee contributors. MIT License.',
                                                                   f'Copyright (c) 2026 {AUTHOR}. Based on Filee (c) Filee contributors. MIT License.')
    write(p, s, o)

# ---- 5. i18n JSON values
for p in sorted(ROOT.rglob("i18n/*.json")):
    if "tests" in p.parts:
        continue
    o = p.read_text(encoding="utf-8"); data = json.loads(o)

    def walk(v):
        if isinstance(v, str):
            return brand(v)
        if isinstance(v, dict):
            return {k: walk(x) for k, x in v.items()}
        if isinstance(v, list):
            return [walk(x) for x in v]
        return v
    s = json.dumps(walk(data), ensure_ascii=False, indent=2) + "\n"
    write(p, s, o)

# ---- 6. build scripts, workflows: executable/package names; docs/installer: links only
for p in list((ROOT / "build").rglob("*.ps1")) + list((ROOT / "build").rglob("*.cs")) + list((ROOT / ".github").rglob("*.yml")):
    s = o = p.read_text(encoding="utf-8"); write(p, brand(s), o)
for p in list((ROOT / "docs").rglob("*.md")) + list((ROOT / "installer").rglob("*")) + [ROOT / "CHANGELOG.md", ROOT / "THIRD-PARTY-NOTICES.md"]:
    if not p.is_file():
        continue
    try:
        s = o = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    s = s.replace("github.com/KnifeLemon/Filee", f"github.com/{GH}/{NEWL}").replace("https://filee.sh/", REPO + "/")
    write(p, s, o)
for name in ("SECURITY.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md"):
    p = ROOT / name; s = o = p.read_text(encoding="utf-8")
    s = brand(s).replace("@KnifeLemon", "@" + GH)
    if name == "CODE_OF_CONDUCT.md":
        s = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", EMAIL, s)
    write(p, s, o)
p = ROOT / ".github/CODEOWNERS"; o = p.read_text(encoding="utf-8"); write(p, o.replace("@KnifeLemon", "@" + GH), o)
f = ROOT / ".github/FUNDING.yml"
if f.exists():
    f.unlink(); rep[".github/FUNDING.yml (deleted)"] += 1
for p in ROOT.glob("README.*.md"):
    p.unlink(); rep[f"{p.name} (deleted)"] += 1
p = ROOT / "LICENSE"; s = o = p.read_text(encoding="utf-8")
if AUTHOR not in s:
    s = re.sub(r"^(Copyright \(c\).*)$", lambda m: f"Copyright (c) 2026 {AUTHOR} ({NEW} modifications)\n" + m.group(1) + " (Filee)", s, count=1, flags=re.M)
write(p, s, o)

print("== files changed:", len(rep))
for k in sorted(rep):
    print("  ", k)
