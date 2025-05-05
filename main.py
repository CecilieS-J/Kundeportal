# Importer nødvendige biblioteker
from webapp import app,db

def main():
      # 1) Opret instance/customer_data.db og alle tabeller
    with app.app_context():
        db.create_all()
    # (valgfrit) udskriv endpoints for hurtigt overblik
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:30s} -> {rule}")
    # start dev-server
    app.run(host='127.0.0.1', port=80, debug=True)
    #app.run(host='0.0.0.0', port=80, debug=True)

# Køres kun hvis scriptet køres direkte
# Hvis scriptet importeres, så køres main ikke
# Dette er en god praksis, da det gør det muligt at genbruge funktioner i andre scripts
# og undgå at køre dem, når scriptet importeres
# Det er også en god måde at sikre, at scriptet kun køres, når det er nødvendigt
if __name__ == "__main__":
    main()

#if __name__ == "__main__":
    # Debug=True mens du udvikler – husk at slå fra i produktion
 #   app.run(host="0.0.0.0", port=80, debug=True)
