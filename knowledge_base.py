
"""
SPORTS_KNOWLEDGE - THE BRAIN'S DATABASE 🧠
Contains tactical profiles and FULL SQUADS for all major teams.
Imported by ai_engine.py to contextualize statistics.

UPDATED: FEB 10, 2026 (Post-Trade Deadline & New Season)
STATUS: VERIFIED
"""

SPORTS_KNOWLEDGE = {
    # ==========================================
    # 🏀 NBA (2026 POST-TRADE DEADLINE)
    # ==========================================
    
    # --- EASTERN CONFERENCE ---
    "celtics": {
        "sport": "Basketball (NBA)",
        "phase": "☘️ Core Mantido",
        "coach": "Joe Mazzulla",
        "key_players": ["Jayson Tatum", "Jaylen Brown", "Jrue Holiday"],
        "squad": ["Jayson Tatum", "Jaylen Brown", "Jrue Holiday", "Derrick White", "Al Horford", "Payton Pritchard", "Luke Kornet"],
        "details": "Mantiveram a base campeã, mas sem Porzingis. Foco total em Tatum e Brown."
    },
    "cavs": {
        "sport": "Basketball (NBA)",
        "phase": "⚔️ The Beard era",
        "coach": "Kenny Atkinson",
        "key_players": ["James Harden", "Donovan Mitchell", "Evan Mobley"],
        "squad": ["James Harden", "Donovan Mitchell", "Evan Mobley", "Jarrett Allen", "Caris LeVert", "Max Strus", "Isaac Okoro"],
        "details": "James Harden chegou para organizar o jogo. Mitchell foca na pontuação. Candidatos ao título."
    },
    "bucks": {
        "sport": "Basketball (NBA)",
        "phase": "🦌 Fear the Deer",
        "coach": "Doc Rivers",
        "key_players": ["Giannis Antetokounmpo", "Damian Lillard", "Khris Middleton"],
        "squad": ["Giannis Antetokounmpo", "Damian Lillard", "Brook Lopez", "Khris Middleton", "Bobby Portis", "Gary Trent Jr."],
        "details": "Elenco reformulado, mas o Big 3 continua. Pressão enorme por resultados."
    },
    "wizards": {
        "sport": "Basketball (NBA)",
        "phase": "🧙‍♂️ Blockbuster",
        "coach": "Brian Keefe",
        "key_players": ["Anthony Davis", "Kyle Kuzma", "Jordan Poole"],
        "squad": ["Anthony Davis", "Kyle Kuzma", "Jordan Poole", "Alex Sarr", "Malcolm Brogdon", "Jonas Valanciunas", "Corey Kispert"],
        "details": "CHOQUE: Anthony Davis no Wizards. O time muda de patamar defensivo e ofensivo instantaneamente."
    },
    "pacers": {
        "sport": "Basketball (NBA)",
        "phase": "🏎️ Pace & Paint",
        "coach": "Rick Carlisle",
        "key_players": ["Tyrese Haliburton", "Pascal Siakam", "Ivica Zubac"],
        "squad": ["Tyrese Haliburton", "Pascal Siakam", "Ivica Zubac", "Myles Turner", "Obi Toppin", "Andrew Nembhard", "TJ McConnell"],
        "details": "Zubac traz proteção de aro que faltava. Haliburton continua maestro."
    },
    "pistons": {
        "sport": "Basketball (NBA)",
        "phase": "⚙️ Rising Force",
        "coach": "J.B. Bickerstaff",
        "key_players": ["Cade Cunningham", "Jaden Ivey", "Jalen Duren"],
        "squad": ["Cade Cunningham", "Jaden Ivey", "Jalen Duren", "Tobias Harris", "Ausar Thompson", "Isaiah Stewart", "Ron Holland"],
        "details": "Liderando a conferência (Surpresa). Cade Cunningham nível MVP."
    },
    "knicks": {
        "sport": "Basketball (NBA)",
        "phase": "🛡️ New York Gritty",
        "coach": "Tom Thibodeau",
        "key_players": ["Jalen Brunson", "Karl-Anthony Towns", "OG Anunoby"],
        "squad": ["Jalen Brunson", "Karl-Anthony Towns", "OG Anunoby", "Mikal Bridges", "Josh Hart", "Mitchell Robinson"],
        "details": "Villanova Knicks + KAT. Time físico e de muita defesa."
    },
    "sixers": {
        "sport": "Basketball (NBA)",
        "phase": "🏥 Processo Infinito",
        "coach": "Nick Nurse",
        "key_players": ["Joel Embiid", "Tyrese Maxey", "Paul George"],
        "squad": ["Joel Embiid", "Tyrese Maxey", "Paul George", "Kelly Oubre Jr.", "Caleb Martin", "Andre Drummond"],
        "details": "Embiid precisa ficar saudável. Paul George é a terceira estrela de luxo."
    },
     "heat": {
        "sport": "Basketball (NBA)",
        "phase": "🔥 Culture",
        "coach": "Erik Spoelstra",
        "key_players": ["Jimmy Butler", "Bam Adebayo", "Tyler Herro"],
        "squad": ["Jimmy Butler", "Bam Adebayo", "Tyler Herro", "Terry Rozier", "Jaime Jaquez Jr.", "Nikola Jovic"],
        "details": "Nunca duvide do Heat. Butler guarda energia para momentos decisivos."
    },
    "magic": {
        "sport": "Basketball (NBA)",
        "phase": "🏰 Magic Kingdom",
        "coach": "Jamahl Mosley",
        "key_players": ["Paolo Banchero", "Franz Wagner", "Jalen Suggs"],
        "squad": ["Paolo Banchero", "Franz Wagner", "Jalen Suggs", "Wendell Carter Jr.", "KCP", "Jonathan Isaac"],
        "details": "Defesa jovem e gigante. Banchero é superestrela em ascensão."
    },
    "hawks": {
        "sport": "Basketball (NBA)",
        "phase": "🦅 Trae's Show",
        "coach": "Quin Snyder",
        "key_players": ["Trae Young", "Jalen Johnson", "Clint Capela"],
        "squad": ["Trae Young", "Jalen Johnson", "Clint Capela", "Bogdan Bogdanovic", "Dyson Daniels", "Onyeka Okongwu"],
        "details": "Ataque rápido, defesa suspeita. Trae Young dita o ritmo."
    },
    "nets": {
        "sport": "Basketball (NBA)",
        "phase": "🏗️ Rebuild",
        "coach": "Jordi Fernández",
        "key_players": ["Cam Thomas", "Nic Claxton", "Dennis Schroder"],
        "squad": ["Cam Thomas", "Nic Claxton", "Dennis Schroder", "Cameron Johnson", "Ben Simmons"],
        "details": "Cam Thomas pontua muito, mas o time vence pouco."
    },
    "raptors": {
        "sport": "Basketball (NBA)",
        "phase": "🦖 North Side",
        "coach": "Darko Rajakovic",
        "key_players": ["Scottie Barnes", "RJ Barrett", "Immanuel Quickley"],
        "squad": ["Scottie Barnes", "RJ Barrett", "Immanuel Quickley", "Jakob Poeltl", "Gradey Dick"],
        "details": "Scottie Barnes faz tudo. Time em desenvolvimento."
    },
    "hornets": {
        "sport": "Basketball (NBA)",
        "phase": "🐝 Buzz",
        "coach": "Charles Lee",
        "key_players": ["LaMelo Ball", "Brandon Miller", "Miles Bridges"],
        "squad": ["LaMelo Ball", "Brandon Miller", "Miles Bridges", "Mark Williams", "Josh Green"],
        "details": "LaMelo saudável é showtime. Brandon Miller pontuador nato."
    },
     "bulls": {
        "sport": "Basketball (NBA)",
        "phase": "🐂 Windy City",
        "coach": "Billy Donovan",
        "key_players": ["Zach LaVine", "Coby White", "Josh Giddey"],
        "squad": ["Zach LaVine", "Nikola Vucevic", "Josh Giddey", "Coby White", "Patrick Williams"],
        "details": "Time de meio de tabela. Giddey organiza, LaVine finaliza."
    },

    # --- WESTERN CONFERENCE ---
    "warriors": {
        "sport": "Basketball (NBA)",
        "phase": "🌉 Splash Tower",
        "coach": "Steve Kerr",
        "key_players": ["Stephen Curry", "Kristaps Porzingis", "Draymond Green"],
        "squad": ["Stephen Curry", "Draymond Green", "Kristaps Porzingis", "Andrew Wiggins", "Buddy Hield", "Jonathan Kuminga"],
        "details": "Splash Brothers mudaram. Porzingis traz o espaçamento vertical que o Curry sonhava."
    },
    "lakers": {
        "sport": "Basketball (NBA)",
        "phase": "👑 King & Reaves",
        "coach": "JJ Redick",
        "key_players": ["LeBron James", "Austin Reaves", "D'Angelo Russell"],
        "squad": ["LeBron James", "Austin Reaves", "D'Angelo Russell", "Rui Hachimura", "Jarred Vanderbilt", "Gabe Vincent"],
        "details": "Sem Anthony Davis (Trocado). LeBron terá que carregar ainda mais carga ofensiva."
    },
    "clippers": {
        "sport": "Basketball (NBA)",
        "phase": "⛵ New Era",
        "coach": "Tyronn Lue",
        "key_players": ["Kawhi Leonard", "Darius Garland", "Bennedict Mathurin"],
        "squad": ["Kawhi Leonard", "Darius Garland", "Bennedict Mathurin", "Terance Mann", "Ivica Zubac", "Derrick Jones Jr."],
        "details": "Garland é o novo armador. Mathurin traz juventude e pontos. Harden saiu."
    },
    "jazz": {
        "sport": "Basketball (NBA)",
        "phase": "🎷 Block Party",
        "coach": "Will Hardy",
        "key_players": ["Lauri Markkanen", "Jaren Jackson Jr.", "Collin Sexton"],
        "squad": ["Lauri Markkanen", "Jaren Jackson Jr.", "Walker Kessler", "Collin Sexton", "John Collins"],
        "details": "Garrafão assustador com JJJ e Kessler. Markkanen pontuador de elite."
    },
    "thunder": {
        "sport": "Basketball (NBA)",
        "phase": "⚡ Young Kings",
        "coach": "Mark Daigneault",
        "key_players": ["Shai Gilgeous-Alexander", "Chet Holmgren", "Jalen Williams"],
        "squad": ["Shai Gilgeous-Alexander", "Chet Holmgren", "Jalen Williams", "Isaiah Hartenstein", "Lu Dort", "Alex Caruso"],
        "details": "Líderes do Oeste. SGA nível MVP. Defesa e ataque equilibrados."
    },
    "mavs": {
        "sport": "Basketball (NBA)",
        "phase": "🐴 Luka Magic",
        "coach": "Jason Kidd",
        "key_players": ["Luka Doncic", "Kyrie Irving", "Klay Thompson"],
        "squad": ["Luka Doncic", "Kyrie Irving", "Klay Thompson", "Dereck Lively II", "PJ Washington"],
        "details": "Perderam peças na trade deadline, mas o trio Luka-Kyrie-Klay segue intacto."
    },
    "nuggets": {
        "sport": "Basketball (NBA)",
        "phase": "🏔️ Joker",
        "coach": "Michael Malone",
        "key_players": ["Nikola Jokic", "Jamal Murray", "Michael Porter Jr"],
        "squad": ["Nikola Jokic", "Jamal Murray", "Aaron Gordon", "Michael Porter Jr.", "Russell Westbrook", "Christian Braun"],
        "details": "Jokic é o sistema. Westbrook traz energia do banco."
    },
    "wolves": {
        "sport": "Basketball (NBA)",
        "phase": "🐺 Ant-Man",
        "coach": "Chris Finch",
        "key_players": ["Anthony Edwards", "Rudy Gobert", "Julius Randle"],
        "squad": ["Anthony Edwards", "Rudy Gobert", "Julius Randle", "Mike Conley", "Naz Reid", "Jaden McDaniels"],
        "details": "Defesa de elite. Edwards é a cara da franquia."
    },
    "suns": {
        "sport": "Basketball (NBA)",
        "phase": "☀️ Firepower",
        "coach": "Mike Budenholzer",
        "key_players": ["Kevin Durant", "Devin Booker", "Bradley Beal"],
        "squad": ["Kevin Durant", "Devin Booker", "Bradley Beal", "Jusuf Nurkic", "Tyus Jones", "Grayson Allen"],
        "details": "Muito talento ofensivo. Defesa é a interrogação."
    },
    "pelicans": {
        "sport": "Basketball (NBA)",
        "phase": "⚜️ Wings",
        "coach": "Willie Green",
        "key_players": ["Zion Williamson", "Brandon Ingram", "CJ McCollum"],
        "squad": ["Zion Williamson", "Brandon Ingram", "CJ McCollum", "Dejounte Murray", "Herb Jones", "Trey Murphy III"],
        "details": "Zion saudável é imparável. Dejounte Murray organiza o time."
    },
    "rockets": {
        "sport": "Basketball (NBA)",
        "phase": "🚀 Lift Off",
        "coach": "Ime Udoka",
        "key_players": ["Alperen Sengun", "Jalen Green", "Fred VanVleet"],
        "squad": ["Alperen Sengun", "Jalen Green", "Fred VanVleet", "Amen Thompson", "Jabari Smith Jr.", "Dillon Brooks"],
        "details": "Time chato e físico. Sengun é o hub ofensivo."
    },
    "grizzlies": {
        "sport": "Basketball (NBA)",
        "phase": "🐻 Grunt",
        "coach": "Taylor Jenkins",
        "key_players": ["Ja Morant", "Desmond Bane", "Marcus Smart"],
        "squad": ["Ja Morant", "Desmond Bane", "Marcus Smart", "Zach Edey", "GG Jackson", "Brandon Clarke"],
        "details": "Sem JJJ (Trocado). Ja Morant tem que assumir tudo. Edey rookie do ano?"
    },
    "spurs": {
        "sport": "Basketball (NBA)",
        "phase": "👽 Alien",
        "coach": "Gregg Popovich",
        "key_players": ["Victor Wembanyama", "Chris Paul", "Devin Vassell"],
        "squad": ["Victor Wembanyama", "Chris Paul", "Devin Vassell", "Jeremy Sochan", "Harrison Barnes", "Stephon Castle"],
        "details": "Wembanyama evoluindo a cada jogo. CP3 mentor."
    },
    "kings": {
        "sport": "Basketball (NBA)",
        "phase": "🟣 Light the Beam",
        "coach": "Mike Brown",
        "key_players": ["De'Aaron Fox", "Domantas Sabonis", "DeMar DeRozan"],
        "squad": ["De'Aaron Fox", "Domantas Sabonis", "DeMar DeRozan", "Keegan Murray", "Malik Monk", "Kevin Huerter"],
        "details": "Ataque rápido e eficiente. Sabonis máquina de rebotes."
    },
    "blazers": {
        "sport": "Basketball (NBA)",
        "phase": "🌧️ Rebuild",
        "coach": "Chauncey Billups",
        "key_players": ["Anfernee Simons", "Scoot Henderson", "Deandre Ayton"],
        "squad": ["Anfernee Simons", "Scoot Henderson", "Jerami Grant", "Deandre Ayton", "Shaedon Sharpe", "Donovan Clingan"],
        "details": "Jovens talentosos mas inexperientes. Scoot Henderson melhorando."
    },


    # ==========================================
    # ⚽ FUTEBOL (SUL-AMERICANO 2026)
    # ==========================================

    # --- BRASILEIRÃO SÉRIE A ---
    "santos": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🐳 O Retorno do Rei",
        "coach": "Fábio Carille",
        "key_players": ["Neymar (Treinando)", "Gabigol", "João Schmidt"],
        "squad": ["Neymar (Speculated/Training)", "Gabriel Barbosa (Gabigol)", "Rony", "João Schmidt", "João Paulo", "Giuliano", "Pituca", "Gil", "Otero"],
        "details": "Promovido como Campeão da B. Gabigol e Neymar (especulado/treino) trazem status estelar."
    },
    "flamengo": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🔴⚫ Malvadão",
        "coach": "Filipe Luís",
        "key_players": ["Pedro", "De La Cruz", "Gerson"],
        "squad": ["Pedro", "Gerson", "Arrascaeta", "De La Cruz", "Léo Pereira", "Rossi", "Bruno Henrique", "Luiz Araújo", "Viña", "Léo Ortiz", "Allan", "Pulgar"],
        "details": "Elenco mais caro. Favorito em tudo."
    },
    "palmeiras": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🐷 Academia",
        "coach": "Abel Ferreira",
        "key_players": ["Estêvão", "Raphael Veiga", "Felipe Anderson"],
        "squad": ["Estêvão", "Raphael Veiga", "Felipe Anderson", "Aníbal Moreno", "Weverton", "Gómez", "Murilo", "Piquerez", "Zé Rafael", "Rony", "Flaco López", "Maurício"],
        "details": "Estêvão continua desequilibrando. Abel busca mais um título."
    },
    "botafogo": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🔥 Glorioso",
        "coach": "Artur Jorge",
        "key_players": ["Thiago Almada", "Luiz Henrique", "Igor Jesus"],
        "squad": ["Luiz Henrique", "Thiago Almada", "Igor Jesus", "John", "Bastos", "Barboza", "Marlon Freitas", "Gregore", "Savarino", "Tiquinho Soares", "Júnior Santos", "Vitinho"],
        "details": "Ataque devastador com Almada e Luiz Henrique."
    },
    "corinthians": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🦅 Timão",
        "coach": "Ramón Díaz",
        "key_players": ["Memphis Depay", "Rodrigo Garro", "Yuri Alberto"],
        "squad": ["Memphis Depay", "Rodrigo Garro", "Yuri Alberto", "Hugo Souza", "André Ramalho", "Fagner", "Carrillo", "José Martínez", "Breno Bidon", "Talles Magno"],
        "details": "Memphis Depay é a estrela. Garro comanda o meio."
    },
    "são paulo": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🇾🇪 Soberano",
        "coach": "Luis Zubeldía",
        "key_players": ["Lucas Moura", "Calleri", "Luciano"],
        "squad": ["Lucas Moura", "Calleri", "Luciano", "Rafael", "Arboleda", "Rafinha", "Luiz Gustavo", "Bobadilla", "Ferreira", "Wellington Rato", "Alan Franco"],
        "details": "Força no Morumbi. Calleri é guerreiro."
    },
    "internacional": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🇦🇹 Inter",
        "coach": "Roger Machado",
        "key_players": ["Rafael Borré", "Alan Patrick", "Enner Valencia"],
        "squad": ["Rafael Borré", "Alan Patrick", "Enner Valencia", "Thiago Maia", "Rochet", "Vitão", "Mercado", "Wesley", "Wanderson", "Fernando"],
        "details": "Ataque perigoso com Borré e Valencia."
    },
    "atlético-mg": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🐔 Galo",
        "coach": "Gabriel Milito",
        "key_players": ["Hulk", "Paulinho", "Gustavo Scarpa"],
        "squad": ["Hulk", "Paulinho", "Gustavo Scarpa", "Arana", "Everson", "Battaglia", "Otávio", "Bernard", "Deyverson", "Zaracho", "Lyanco"],
        "details": "Hulk e Paulinho: dupla letal."
    },
    "cruzeiro": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🦊 Cabuloso",
        "coach": "Fernando Diniz",
        "key_players": ["Matheus Pereira", "Kaio Jorge", "Cássio"],
        "squad": ["Cássio", "Matheus Pereira", "Kaio Jorge", "Gabriel Veron", "William", "Marlon", "Lucas Romero", "Walace", "Matheus Henrique", "Lautaro Díaz"],
        "details": "Matheus Pereira é o dono do time."
    },
    "grêmio": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🇪🇪 Tricolor Gaúcho",
        "coach": "Renato Gaúcho",
        "key_players": ["Braithwaite", "Cristaldo", "Soteldo"],
        "squad": ["Braithwaite", "Monsalve", "Cristaldo", "Soteldo", "Villasanti", "Marchesín", "Kannemann", "Jemerson", "Diego Costa", "Reinaldo"],
        "details": "Braithwaite trouxe gols. Renato comanda o vestiário."
    },
    "vasco": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "💢 Gigante",
        "coach": "Rafael Paiva",
        "key_players": ["Philippe Coutinho", "Vegetti", "Payet"],
        "squad": ["Philippe Coutinho", "Vegetti", "Payet", "Lucas Piton", "Léo Jardim", "João Victor", "Maicon", "Hugo Moura", "Adson", "David"],
        "details": "Coutinho e Payet na criação. Vegetti finaliza."
    },
    "bahia": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🔵 Esquadrão",
        "coach": "Rogério Ceni",
        "key_players": ["Everton Ribeiro", "Cauly", "Jean Lucas"],
        "squad": ["Everton Ribeiro", "Cauly", "Jean Lucas", "Luciano Juba", "Thaciano", "Caio Alexandre", "Marcos Felipe", "Santiago Arias", "Kanu", "Ademir"],
        "details": "Time técnico e de posse de bola."
    },
    "fluminense": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🇭🇺 Flu",
        "coach": "Mano Menezes",
        "key_players": ["Thiago Silva", "Ganso", "Jhon Arias"],
        "squad": ["Thiago Silva", "Ganso", "Jhon Arias", "Kevin Serna", "Kauã Elias", "Fábio", "Marcelo", "Cano", "Keno", "Martinelli", "Bernal"],
        "details": "Thiago Silva lidera a defesa. Arias é o motor."
    },
    "athletico-pr": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🌪️ Furacão (Promovido)",
        "coach": "Lucho González",
        "key_players": ["Fernandinho", "Mastriani", "Canobbio"],
        "squad": ["Fernandinho", "Mastriani", "Canobbio", "Zapelli", "Thiago Heleno", "Mycael", "Christian", "Esquivel", "Pablo"],
        "details": "De volta à elite. Força na Arena da Baixada."
    },
    "coritiba": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🟢 Coxa (Promovido)",
        "coach": "Jorginho",
        "key_players": ["Robson", "Matheus Frizzo"],
        "squad": ["Robson", "Matheus Frizzo", "Sebastián Gómez", "Natanael", "Bruno Gomes"],
        "details": "Promovido. Luta para permanecer."
    },
    "chapecoense": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🏹 Chape (Promovido)",
        "coach": "Umberto Louzer",
        "key_players": ["Mário Sérgio", "Giovanni"],
        "squad": ["Mário Sérgio", "Giovanni", "Matheus Cavichioli"],
        "details": "Retorno histórico à Série A."
    },
    "remo": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🦁 Leão Azul (Promovido)",
        "coach": "Rodrigo Santana",
        "key_players": ["Pedro Rocha", "Ribamar"],
        "squad": ["Pedro Rocha", "Ribamar", "Jaderson", "Marcelo Rangel"],
        "details": "A grande surpresa da temporada. Força do Norte."
    },
    "mirassol": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🟡 Leão da Alta (Promovido)",
        "coach": "Mozart",
        "key_players": ["Dellatorre", "Negueba"],
        "squad": ["Dellatorre", "Negueba", "Fernandinho", "Alex Muralha"],
        "details": "Clube empresa organizado. Estreia na elite."
    },
    "bragantino": {
        "sport": "Football (Brasileirão Série A)",
        "phase": "🐂 Massa Bruta",
        "coach": "Pedro Caixinha",
        "key_players": ["Eduardo Sasha", "Helinho", "Cleiton"],
        "squad": ["Eduardo Sasha", "Helinho", "Cleiton", "Juninho Capixaba", "Lucas Evangelista", "Lincoln", "Jadsom", "Mosquera", "Luan Cândido"],
        "details": "Mantém o projeto Red Bull na elite."
    },

    # --- BRASILEIRÃO SÉRIE B ---
    "fortaleza": {
        "sport": "Football (Série B)",
        "phase": "🦁 Leão (Rebaixado)",
        "coach": "Juan Pablo Vojvoda",
        "key_players": ["Lucero", "Pikachu", "Moisés"],
        "squad": ["Lucero", "Pikachu", "Moisés", "João Ricardo", "Tinga", "Brítez", "Pochettino", "Hércules", "Zé Welison", "Marinho"],
        "details": "A grande surpresa negativa. Rebaixado com elenco forte. Favorito absoluto a subir."
    },
    "sport": {
        "sport": "Football (Série B)",
        "phase": "🦁 Leão da Ilha",
        "coach": "Pepa",
        "key_players": ["Gustavo Coutinho", "Lucas Lima"],
        "squad": ["Gustavo Coutinho", "Lucas Lima", "Caíque França", "Castán", "Felipinho", "Barletta", "Zé Roberto"],
        "details": "Bateu na trave de novo. Força na Ilha."
    },
    "ceará": {
        "sport": "Football (Série B)",
        "phase": "👴 Vozão",
        "coach": "Léo Condé",
        "key_players": ["Erick Pulga", "Saulo Mineiro"],
        "squad": ["Erick Pulga", "Saulo Mineiro", "Richard", "Lourenço", "Recalde", "Aylon", "Mugni"],
        "details": "Erick Pulga é o diferencial."
    },
    "juventude": {
        "sport": "Football (Série B)",
        "phase": "🟢 Papo (Rebaixado)",
        "coach": "Jair Ventura",
        "key_players": ["Nenê", "Jean Carlos"],
        "squad": ["Nenê", "Jean Carlos", "Gabriel", "Lucas Barbosa"],
        "details": "Caiu e tenta se reorganizar."
    },
    "goiás": {
        "sport": "Football (Série B)",
        "phase": "🟢 Esmeraldino",
        "coach": "Vagner Mancini",
        "squad": ["Tadeu", "Galhardo", "Messias", "Paulo Baya"],
        "details": "Time tradicional da B."
    },
    "américa-mg": {
        "sport": "Football (Série B)",
        "phase": "🐰 Coelho",
        "coach": "Lisca",
        "squad": ["Juninho", "Benítez", "Moisés"],
        "details": "Sempre briga lá em cima."
    },
    "vila nova": { "sport": "Football (Série B)", "details": "O Tigre busca o acesso inédito." },
    "criciúma": { "sport": "Football (Série B)", "details": "Tigre carvoeiro." },
    "avaí": { "sport": "Football (Série B)", "details": "Leão da Ilha (SC)." },
    "ponte preta": { "sport": "Football (Série B)", "details": "Macaca de Campinas." },
    "novorizontino": { "sport": "Football (Série B)", "details": "Tigre do Vale." },
    "crb": { "sport": "Football (Série B)", "details": "Galo da Pajuçara." },
    "botafogo-sp": { "sport": "Football (Série B)", "details": "Pantera." },
    "cuiabá": { "sport": "Football (Série B)", "details": "Dourado (Rebaixado)." },
    "operário-pr": { "sport": "Football (Série B)", "details": "Fantasma." },
    "amazonas": { "sport": "Football (Série B)", "details": "Onça Pintada." },
    "paysandu": { "sport": "Football (Série B)", "details": "Papão da Curuzu." },
    "ituano": { "sport": "Football (Série B)", "details": "Galo de Itu." },
    "brusque": { "sport": "Football (Série B)", "details": "Quadricolor." },
    "guarani": { "sport": "Football (Série B)", "details": "Bugre." }
}
