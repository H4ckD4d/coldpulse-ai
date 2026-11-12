"""Command-line entry point for ColdPulse AI."""
import argparse
import json
from . import core, research

PUBLIC_TOPICS = {
"pt": "Boas práticas públicas de telemetria e detecção de anomalias hvac-r",
"en": "Public best practices for hvac-r telemetry and anomaly detection",
"es": "Buenas prácticas públicas sobre telemetría y detección de anomalías hvac-r"}

def main():
    parser = argparse.ArgumentParser(description="ColdPulse AI by Chris Cruz (@h4ckd4d)")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="Run local, synthetic demonstration")
    demo.add_argument("--lang", choices=["pt", "en", "es"], default="pt")
    external = sub.add_parser("research", help="Opt-in public research grounded with Google Search")
    external.add_argument("--lang", choices=["pt", "en", "es"], default="pt")
    external.add_argument("--topic", default=None)
    core.configure(sub)
    args = parser.parse_args()
    if args.command == "demo":
        result = core.demo()
    elif args.command == "research":
        result = research.lookup(args.topic or PUBLIC_TOPICS[args.lang], args.lang)
    else:
        result = core.run(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
