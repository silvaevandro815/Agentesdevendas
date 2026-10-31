"""
=============================================================================
MATRIZ OFICIAL DOS 31 TEMAS & 31 CENÁRIOS FITNESS - MARCÃO PERSONAL
=============================================================================
- 31 temas distintos de Saúde, Treino, Nutrição, Biomecânica e Fisiologia.
- 31 cenários/locais cinematográficos únicos (1 para cada dia do mês).
- Rotação estrita: um tema/cenário por dia, só repetindo após os outros 30.
- Vinculação com produtos reais do catálogo (Balança Shopee, Creatina,
  Colágeno, Joelheira, Cinto Lombar, Elásticos, Straps, Compressão, Strava).
=============================================================================
"""

MATRIZ_31_DIAS = [
    {
        "dia": 1,
        "id": "dia01_balanca_bioimpedancia_13",
        "titulo": "A Balança Comum Mente pra Você: 13 Biomarcadores",
        "categoria": "BIOMETRIA & CIÊNCIA",
        "produto": "Balança Inteligente Shopee Bluetooth BIA (R$ 34,90)",
        "link_venda": "https://s.shopee.com.br/2BFoInIBeb",
        "preco": "R$ 34,90",
        "custo_dia": "R$ 0,09 / dia",
        "cenario_nome": "Living Room Minimalista de Luxo ao Amanhecer",
        "cenario_detalhe": "Living room amplo e clean com piso de madeira nobre, grandes janelas de vidro do chão ao teto com luz natural da manhã suave, plantas costela-de-adão decorativas, balança preta slim com display LED azul brilhante no chão.",
        "prompt_cenario_runpod": "Luxury modern minimalist sunlit living room, floor-to-ceiling windows with soft morning sunlight, polished dark hardwood floors, sleek black smart bioimpedance scale with illuminated blue LED display on the floor, cinematic lighting, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina, handsome Brazilian man with short neat dark hair, athletic physique, wearing minimalist black training shorts, stepping barefoot onto the sleek black bioimpedance scale, holding smartphone syncing clinical health metrics, confident focus",
        "script": "Parou de emagrecer na balança comum? Cuidado, meu parceiro! Ela só mede peso bruto e pode estar mentindo. A nossa balança inteligente escaneia 13 biomarcadores na hora e ainda destrava 90 dias de mentoria VIP comigo no WhatsApp!",
        "subtitles": [
            {"start": 0.3, "end": 4.8, "text": "A BALANÇA COMUM MENTE PRA VOCÊ!", "color": "white", "size": 52},
            {"start": 4.9, "end": 10.2, "text": "13 BIOMARCADORES LIDOS NA HORA!", "color": "gold", "size": 50},
            {"start": 10.3, "end": 15.8, "text": "DESTRAVE SUA MENTORIA VIP NA SHOPEE!", "color": "white", "size": 48}
        ],
        "template_hyperframes": "marcao_balanca_bioimpedancia",
        "caption": """⚖️ A BALANÇA COMUM DE FARMÁCIA ESTÁ MENTINDO PRA VOCÊ!

Balança comum é "cega": se você perder 2kg de músculo e reter água suja, ela diz que você emagreceu. Mentira! O músculo é muito mais denso que a gordura.

A Balança Inteligente de Bioimpedância da Shopee (por apenas R$ 34,90, menos de R$ 0,09/dia!) faz a leitura de 13 biomarcadores em 3 segundos:
📊 % de Gordura Real e Massa Muscular
⚠️ Nível de Gordura Visceral (órgãos internos)
💧 Hidratação Celular e Taxa Metabólica Basal (TMB)

🎁 E tem mais: comprando pelo link oficial, você destrava o meu acompanhamento VIP no WhatsApp!

🔗 Garanta a sua no link da Bio por R$ 34,90: marcaopersonal.com

#marcao #marcaopersonal #bioimpedancia #balancainteligente #emagrecimento #massamagra #fitness"""
    },
    {
        "dia": 2,
        "id": "dia02_creatina_atp_forca",
        "titulo": "Creatina Não É Retenção de Líquido: A Via do ATP",
        "categoria": "SUPLEMENTAÇÃO & FORÇA",
        "produto": "Creatina Micronizada 100% Pura Nature's Prime",
        "link_venda": "https://ev.braip.com/ref?pl=pla1x6xn&ck=chen80rq&af=afimeno621",
        "preco": "R$ 169,90",
        "custo_dia": "R$ 1,68 / dia",
        "cenario_nome": "Academia de Ferro com Iluminação Neon Âmbar",
        "cenario_detalhe": "Academia moderna de ferro com iluminação neon âmbar e preta, racks de halteres emborrachados pesados alinhados em perspectiva profunda, espelhos escuros com reflexos dinâmicos.",
        "prompt_cenario_runpod": "High-end modern bodybuilding gym, dramatic amber and cyan neon rim lighting, rows of heavy black matte dumbbells on steel racks, dark reflective floor, raw athletic intensity, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina, Brazilian athletic man with short dark hair, wearing sleek black compression shirt, holding a heavy dumbbell during intense workout, vascular forearms, powerful athletic posture, determination",
        "script": "Ainda acha que creatina incha o corpo ou faz mal pro rim? Mito puro! A creatina joga água só dentro do músculo pra ressintetizar ATP. Você ganha vinte por cento mais força de verdade por menos de dois reais por dia!",
        "subtitles": [
            {"start": 0.3, "end": 4.5, "text": "CREATINA NÃO INCHA O CORPO!", "color": "white", "size": 52},
            {"start": 4.6, "end": 9.8, "text": "+28% DE FORÇA REAL NA VIA DO ATP!", "color": "gold", "size": 50},
            {"start": 9.9, "end": 15.0, "text": "APENAS R$ 1,68 POR DIA!", "color": "white", "size": 52}
        ],
        "template_hyperframes": "marcao_creatina_science",
        "caption": """⚡ O MITO DA CREATINA QUE ESTÁ TRAVANDO SUA FORÇA!

"Marcão, creatina retém líquido e deixa roliço?" Mentira de quem não lê ciência!
A creatina puxa água exclusivamente para o meio INTRACELULAR das fibras musculares (sarcoplasma), sinalizando síntese proteica acelerada e fornecendo fosfato para a ressíntese explosiva de ATP.

Você não incha: você treina mais pesado, fadiga menos e ganha até +28% de força real!

💡 Custo de apenas R$ 1,68 por dia (menos que meio cafezinho na padaria!).

🔗 Garanta a Creatina Micronizada 100% Pura no link da Bio: marcaopersonal.com

#marcao #creatina #hipertrofia #treinodeforca #musculacao #suplementos #suplementacao"""
    },
    {
        "dia": 3,
        "id": "dia03_joelho_tendao_colageno",
        "titulo": "Joelho Estalando no Agachamento: Cartilagem e Tendão",
        "categoria": "SAÚDE ARTICULAR & PREVENÇÃO",
        "produto": "Joelheira de Compressão Neoprene Shopee + Colágeno com Hialurônico",
        "link_venda": "https://s.shopee.com.br/AUvD3t2pKw",
        "preco": "R$ 29,90",
        "custo_dia": "R$ 0,16 / dia",
        "cenario_nome": "Box de Cross-Training com Piso Emborrachado e Barras Olímpicas",
        "cenario_detalhe": "Box de cross-training com piso emborrachado preto de alta densidade, barras olímpicas com anilhas de competição, magnésio suspenso na luz solar rasante, atmosfera rústica e forte.",
        "prompt_cenario_runpod": "Authentic cross-training strength warehouse, dark rubberized floor, steel Olympic barbell with heavy bumper plates, atmospheric chalk dust in sunbeams, cinematic sports arena, 8k vertical 9:16",
        "persona_tipo": "neutro_atleta",
        "prompt_persona": "Athletic Brazilian competitor sitting on plyo box, pulling on professional black and cyan neoprene knee sleeve tightly over the knee, muscular quadriceps, focused pre-squat concentration",
        "script": "Joelho estalando ao agachar ou doendo depois do leg press? Músculo forte com tendão inflamado não dura! A joelheira de compressão dissipa a carga e o colágeno regenera a cartilagem pra você agachar sem dor!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "JOELHO ESTALANDO AO AGACHAR?", "color": "white", "size": 52},
            {"start": 4.7, "end": 9.8, "text": "BLINDE O TENDÃO PATELAR COM COMPRESSÃO!", "color": "gold", "size": 48},
            {"start": 9.9, "end": 15.2, "text": "TREINE PESADO SEM MEDO DE LESÃO!", "color": "white", "size": 50}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """🦵 JOELHO ESTALANDO NO AGACHAMENTO? NÃO IGNORE ESSE SINAL!

A cartilagem articular não tem vasos sanguíneos diretos: ela depende de compressão elástica térmica e nutrição de peptídeos bioativos de colágeno para se regenerar. Se você agacha com o joelho frio ou sem sustentação, o tendão patelar sofre microfissuras que viram tendinite crônica.

Como blindar seus joelhos:
1️⃣ Joelheira de Neoprene 7mm: mantém a temperatura sinovial e dissipa o torque lateral.
2️⃣ Colágeno Tipo II com Ácido Hialurônico: lubrifica a cápsula articular.
3️⃣ Pés firmes com 3 pontos de apoio no solo.

🔗 Joelheira Oficial de Compressão na Shopee por R$ 29,90 no link da Bio: marcaopersonal.com

#marcao #joelho #agachamento #articulacoes #legday #prevençãodelesões #musculacao"""
    },
    {
        "dia": 4,
        "id": "dia04_sono_anabolico_gh",
        "titulo": "O Músculo Não Cresce no Treino: O Pico Noturno de GH",
        "categoria": "BIOHACKING & RECUPERAÇÃO",
        "produto": "Complexo Sono Reparador / Magnésio Dimalato + Melatonina",
        "link_venda": "https://ev.braip.com/ref?pl=pla1x6xn&ck=chen80rq&af=afimeno621",
        "preco": "R$ 169,90",
        "custo_dia": "R$ 1,68 / dia",
        "cenario_nome": "Quarto Sofisticado com Cortinas Blackout e Luz Âmbar Relaxante",
        "cenario_detalhe": "Quarto sofisticado com cortinas blackout espessas, iluminação âmbar indireta suave de 2400k, lençóis de linho premium cinza escuro, ambiente minimalista e silencioso projetado para sono profundo.",
        "prompt_cenario_runpod": "Luxury master bedroom interior at night, dark warm ambient lighting, elegant dark wood paneling, blackout curtains, peaceful calm restorative atmosphere, 8k vertical 9:16",
        "persona_tipo": "maduro_grisalho",
        "prompt_persona": "Distinguished fit Brazilian mature man 58 years old with neat grey silver hair, relaxed athletic posture, checking his biometric sleep tracker watch, tranquil peaceful demeanor, recovery mindset",
        "script": "Você pode treinar como um leão, mas se dorme mal, tá jogando seu resultado no lixo! É na fase profunda do sono que o corpo libera oitenta por cento do GH noturno e reconstrói as fibras musculares.",
        "subtitles": [
            {"start": 0.3, "end": 4.7, "text": "O MÚSCULO NÃO CRESCE NO TREINO!", "color": "white", "size": 52},
            {"start": 4.8, "end": 9.9, "text": "80% DO GH É LIBERADO NO SONO REM!", "color": "gold", "size": 50},
            {"start": 10.0, "end": 15.5, "text": "DURMA COM FOCO ANABÓLICO TOTAL!", "color": "white", "size": 50}
        ],
        "template_hyperframes": "marcao_myth_buster",
        "caption": """😴 O SEU MÚSCULO NÃO CRESCE NA ACADEMIA! CRESCE NA CAMA!

No treino você apenas causa microlesões e estresse mecânico. Quem reconstrói o tecido, sintetiza novas miofibrilas e queima gordura visceral é o sono profundo de ondas lentas (Fase REM e NREM 3).

É entre as 23h30 e as 02h00 que a hipófise atinge o pico de liberação do hormônio do crescimento (GH) e a testosterona basal se regenera.

Regras de ouro do Marcão para o sono anabólico:
🌙 Quarto 100% escuro (desligue celular e luz azul 30 min antes).
🧊 Temperatura fresca e ventilada.
⚡ Magnésio Dimalato + Melatonina para relaxamento neuromuscular profundo.

🔗 Conheça o protocolo completo de recuperação: marcaopersonal.com

#marcao #sonoanabolico #hipertrofia #recuperacaomuscular #gh #dormirbem #qualidadedevida"""
    },
    {
        "dia": 5,
        "id": "dia05_cinto_lombar_intraabdominal",
        "titulo": "Pressão Intra-Abdominal e Proteção da Coluna Lombar",
        "categoria": "BIOMECÂNICA DE CARGA",
        "produto": "Cinto de Musculação com Suporte Lombar Reforçado Shopee",
        "link_venda": "https://s.shopee.com.br/4fxQZlKctc",
        "preco": "R$ 49,90",
        "custo_dia": "R$ 0,27 / dia",
        "cenario_nome": "Plataforma de Madeira Maciça de Levantamento Terra",
        "cenario_detalhe": "Plataforma de madeira nobre de levantamento de peso olímpico cercada por anilhas pretas calibradas, rack de agachamento de ferro maciço, iluminação zenital focada na barra.",
        "prompt_cenario_runpod": "Professional Olympic weightlifting wooden platform inside elite gym, heavy iron barbells loaded with black bumper plates, overhead dramatic spotlight, industrial sports arena, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina, Brazilian athletic man with short dark hair, wearing sleek black dry-fit shirt, fastening heavy-duty black lumbar lifting belt around his waist with laser focus, preparing for heavy deadlift",
        "script": "Sentiu pinçamento na lombar depois de agachar pesado? Isso é falta de pressão intra-abdominal! O cinto de musculação cria uma parede rígida pro seu core empurrar, blindando a coluna e destravando mais carga!",
        "subtitles": [
            {"start": 0.3, "end": 4.8, "text": "LOMBAR DOENDO DEPOIS DE AGACHAR?", "color": "white", "size": 52},
            {"start": 4.9, "end": 10.0, "text": "PRESSÃO INTRA-ABDOMINAL BLINDA A COLUNA!", "color": "gold", "size": 48},
            {"start": 10.1, "end": 15.6, "text": "CINTO LOMBAR OFICIAL SHOPEE POR R$ 49,90!", "color": "white", "size": 46}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """🛡️ DOR NA LOMBAR NO TREINO PESADO? O ERRO QUE VOCÊ ESTÁ COMETENDO!

Quando você executa agachamentos, levantamento terra ou remadas curvadas com cargas elevadas, a gravidade comprime os discos intervertebrais L4-L5 e L5-S1.

A Manobra de Valsalva combinada com o Cinto de Musculação cria uma parede de contenção: seu abdômen empurra contra o cinto rígido, aumentando a pressão intra-abdominal em até 40%. O resultado? Sua coluna fica travada como uma viga de concreto armado!

Benefícios do Cinto Reforçado:
✅ Dissipação uniforme do estresse vertebral
✅ Estabilização imediata da pelve
✅ Mais segurança para quebrar recordes de carga

🔗 Cinto Lombar Reforçado na Shopee por apenas R$ 49,90 no link da Bio: marcaopersonal.com

#marcao #lombar #cinturãodelombar #agachamento #deadlift #biomecanica #treinopesado"""
    },
    {
        "dia": 6,
        "id": "dia06_whey_janela_anabolica",
        "titulo": "Proteína de Rápida Absorção e o Gatilho da Via mTOR",
        "categoria": "NUTRIÇÃO & SÍNTESE PROTEICA",
        "produto": "100% Whey Pure Max Titanium / Whey Concentrado DUX",
        "link_venda": "https://marcaopersonal.com#loja",
        "preco": "R$ 99,90",
        "custo_dia": "R$ 3,33 / dose",
        "cenario_nome": "Cozinha Gourmet de Alta Tecnologia com Bancada de Mármore",
        "cenario_detalhe": "Cozinha gourmet de alta tecnologia com bancada de mármore preto Nero Marquina, torneira minimalista de aço escovado, coqueteleira moderna de aço fosco, atmosfera clean e nutricional.",
        "prompt_cenario_runpod": "High-end luxury modern gourmet kitchen, black marble countertops, sleek brushed stainless steel appliances, morning soft sunlight, clean nutrition lifestyle, 8k vertical 9:16",
        "persona_tipo": "mulher_atletica",
        "prompt_persona": "Fit athletic Brazilian woman 30 years old, toned defined arms and shoulders, wearing sleek black sports bra, pouring creamy protein shake into a shaker cup, healthy radiant smile, athletic nutrition focus",
        "script": "Bater proteína mastigando frango o dia todo é difícil, né? O Whey Protein entrega aminoácidos de altíssima biodisponibilidade com leucina pura pra ligar a chave da via mTOR e reconstruir seu músculo na hora!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "DIFICULDADE DE BATER SUA PROTEÍNA?", "color": "white", "size": 52},
            {"start": 4.7, "end": 9.8, "text": "LEUCINA PURA QUE LIGA A VIA mTOR!", "color": "gold", "size": 50},
            {"start": 9.9, "end": 15.0, "text": "WHEY PROTEIN HOMOLOGADO NA BIO!", "color": "white", "size": 52}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """🥩 O GATILHO DA VIA mTOR: POR QUE A PROTEÍNA DEFINE O SEU CORPO?

Se você quer massa magra definida e queima contínua de gordura, seu corpo precisa de no mínimo 1.8g a 2.2g de proteína por kg de peso corporal ao dia.

O Whey Protein não é pó milagroso: é o soro do leite filtrado de altíssimo valor biológico, rico em aminoácidos de cadeia ramificada (especialmente a Leucina). A leucina atua como a chave liga/desliga da via enzimática mTOR no citoplasma da célula, sinalizando o início imediato da síntese de novas proteínas musculares.

Vantagens:
🥛 Absorção rápida sem pesar no estômago
🧁 Mata a vontade de doce sem quebrar a dieta
💪 Protege sua massa muscular durante o déficit calórico

🔗 Marcas homologadas com laudo de pureza no link da Bio: marcaopersonal.com#loja

#marcao #wheyprotein #proteina #massamagra #nutricaoesportiva #dieta #suplementos"""
    },
    {
        "dia": 7,
        "id": "dia07_strava_bpm_cardio",
        "titulo": "Zona 2 Cardíaca: O Segredo Científico da Queima de Gordura",
        "categoria": "TELEMETRIA & CARDIO",
        "produto": "Smartwatch Xiaomi Smart Band 8 com Sincronização Strava",
        "link_venda": "https://marcaopersonal.com#loja",
        "preco": "R$ 189,90",
        "custo_dia": "R$ 0,52 / dia",
        "cenario_nome": "Pista de Atletismo Olímpica ao Ar Livre com Tartã Vermelho",
        "cenario_detalhe": "Pista de atletismo olímpica ao ar livre com curvas de piso sintético vermelho sob névoa matinal e raios de sol dourados nascendo no horizonte, horizonte aberto e inspirador.",
        "prompt_cenario_runpod": "Olympic red tartan running track outdoors at dawn, golden hour morning mist, open sky, professional athletic training venue, cinematic lens flare, 8k vertical 9:16",
        "persona_tipo": "corredor_urbano",
        "prompt_persona": "Lean athletic Brazilian runner in modern charcoal running gear, checking the heart rate telemetry display on his sleek smartwatch screen showing 138 BPM, focused rhythmic breathing, outdoor endurance",
        "script": "Correr até a língua sair pra fora não é o que queima mais gordura! É na Zona Dois de batimentos que suas mitocôndrias usam gordura como combustível puro. Monitore seu cardio no Strava do time Marcão!",
        "subtitles": [
            {"start": 0.3, "end": 4.8, "text": "CORRER DESESPERADO NÃO QUEIMA MAIS!", "color": "white", "size": 50},
            {"start": 4.9, "end": 10.0, "text": "ZONA 2: GORDURA COMO COMBUSTÍVEL PURO!", "color": "gold", "size": 48},
            {"start": 10.1, "end": 15.6, "text": "MONITORE NO STRAVA DO TIME MARCÃO!", "color": "white", "size": 50}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """🏃 O ERRO CLÁSSICO DO CARDIO: POR QUE MENOS É MAIS?

Você sobe na esteira ou sai pra correr e fica quase sem ar, com o coração a 170 BPM achando que tá secando a barriga? Cuidado: nessa frequência cardíaca você está depletando glicogênio e queimando massa magra por catabolismo!

A ciência comprovou: a queima máxima de ácidos graxos por oxidação mitocondrial acontece na ZONA 2 (60% a 70% da sua FC máxima, geralmente entre 125 e 142 BPM). Você consegue conversar enquanto treina e queima gordura pura!

Como aplicar:
⌚ Monitore seus batimentos com um Smartwatch com GPS.
🚴 Mantenha o ritmo constante por 40 a 50 minutos.
📲 Sincronize suas atividades com o clube Marcão no Strava!

🔗 Smartwatch com monitoramento cardíaco homologado na Bio: marcaopersonal.com#loja

#marcao #cardio #zona2 #strava #queimadegordura #corrida #frequenciacardiaca #emagrecimento"""
    },
    {
        "dia": 8,
        "id": "dia08_elasticos_treino_casa",
        "titulo": "Tensão Mecânica Progressiva Sem Sair de Casa",
        "categoria": "TREINO EM CASA & MOBILIDADE",
        "produto": "Kit Elásticos Extensores com Âncora de Porta Shopee",
        "link_venda": "https://s.shopee.com.br/6fiUxRLoRK",
        "preco": "R$ 49,90",
        "custo_dia": "R$ 0,27 / dia",
        "cenario_nome": "Varanda Envidraçada Ampla com Vista Panorâmica Urbana",
        "cenario_detalhe": "Varanda ampla envidraçada de cobertura residencial com piso vinílico amadeirado, luz natural ampla do fim de tarde, kit de elásticos tensores fixados na âncora de porta com segurança.",
        "prompt_cenario_runpod": "Spacious luxury glass-enclosed apartment balcony overlooking modern city skyline at sunset, warm hardwood flooring, clean athletic workout space, cinematic vertical 9:16",
        "persona_tipo": "mulher_atletica",
        "prompt_persona": "Fit Brazilian woman with athletic physique in teal compression tights, performing seated cable-style row with resistance bands anchored to door frame, perfect posture, engaging back muscles",
        "script": "Sem tempo de ir pra academia hoje? Sem desculpa, meu parceiro! O kit de elásticos extensores com âncora de porta cria tensão mecânica progressiva pro corpo todo na sala da sua casa por menos de cinquenta reais!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "SEM TEMPO DE IR PRA ACADEMIA?", "color": "white", "size": 52},
            {"start": 4.7, "end": 9.8, "text": "TENSÃO MECÂNICA PROGRESSIVA EM CASA!", "color": "gold", "size": 48},
            {"start": 9.9, "end": 15.2, "text": "KIT EXTENSOR OFICIAL SHOPEE R$ 49,90!", "color": "white", "size": 48}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """🏠 NÃO TEM TEMPO DE IR PRA ACADEMIA? TRANSFORME SUA CASA NUM CENTRO DE TREINO!

A hipertrofia muscular não sabe se você está puxando um aparelho de 50 mil reais ou um elástico extensor de 49 reais. O que o seu músculo reconhece é TENSÃO MECÂNICA e RECRUTAMENTO DE UNIDADES MOTORAS.

Com a curva de resistência ascendente do elástico, quanto mais você puxa, mais pesada a carga fica no pico da contração!

O que você faz com o Kit de Elásticos Shopee:
💪 Supino e crucifixo para peitoral
🦁 Puxadas altas e remadas para costas densas
🦵 Agachamentos e passadas com sobrecarga constante
🚀 Braços, ombros e abdômen completos

🔗 Kit Completo com 5 tensões, alças e âncora por R$ 49,90 no link da Bio: marcaopersonal.com

#marcao #treinoemcasa #elasticosextensores #calistenia #musculacaoemcasa #disciplina"""
    },
    {
        "dia": 9,
        "id": "dia09_straps_dorsal_isometria",
        "titulo": "Antebraço Falhando Antes da Dorsal? O Segredo do Strap",
        "categoria": "BIOMECÂNICA DE TRAÇÃO",
        "produto": "Strap de Algodão Reforçado com Neoprene Shopee",
        "link_venda": "https://s.shopee.com.br/2BG5b2xhm2",
        "preco": "R$ 19,90",
        "custo_dia": "R$ 0,11 / dia",
        "cenario_nome": "Área de Puxadas Altas e Cabos em Academia Moderna",
        "cenario_detalhe": "Área de puxadas altas e remadas com cabos pesados em academia moderna, barra cromada refletindo luzes de teto, placas de peso de 120kg travadas no pino de carga.",
        "prompt_cenario_runpod": "High-end gym cable crossover and lat pulldown station, heavy chrome weight stacks, dark moody steel aesthetic, intense focused training zone, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina, Brazilian athletic man with short dark hair, wearing sleek black compression shirt, tightly wrapping black cotton lifting strap around heavy lat pulldown bar, laser focus, vascular arms",
        "script": "Faz puxada ou remada e o antebraço queima antes da asa das costas cansar? Isso mata a sua dorsal! O strap de algodão trava a barra na sua mão pra você esmagar as costas com carga máxima de verdade!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "ANTEBRAÇO FALHANDO ANTES DA DORSAL?", "color": "white", "size": 50},
            {"start": 4.7, "end": 9.9, "text": "ISOLAMENTO CIRÚRGICO DAS COSTAS!", "color": "gold", "size": 52},
            {"start": 10.0, "end": 15.0, "text": "STRAP OFICIAL SHOPEE POR R$ 19,90!", "color": "white", "size": 50}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """🦁 ANTEBRAÇO FALHA ANTES DAS COSTAS? PARE DE PERDER DORSAL!

Os músculos flexores dos dedos e do antebraço são pequenos e têm pouca reserva de glicogênio comparados ao latíssimo do dorso (que é um dos maiores músculos do corpo humano).

Se você faz remadas ou puxadas sem strap, sua pegada abre antes do grande dorsal atingir a sobrecarga progressiva ideal.

O Strap com Neoprene Shopee:
🔒 Transfere a força diretamente para as costas
💥 Permite usar de 20% a 30% mais carga nas puxadas
🛡️ Protege o punho com almofada interna confortável

🔗 Garanta o seu par na Shopee por apenas R$ 19,90 no link da Bio: marcaopersonal.com

#marcao #strap #dorsal #treinodecostas #musculacao #puxada #hipertrofia #shopee"""
    },
    {
        "dia": 10,
        "id": "dia10_omega3_antioxidante_dha",
        "titulo": "Inflamação Articular Silenciosa e Ácidos Graxos EPA/DHA",
        "categoria": "SAÚDE CARDIOVASCULAR & ANTI-INFLAMATÓRIA",
        "produto": "Ômega 3 Ultra Concentrado EPA/DHA Nature's Prime",
        "link_venda": "https://marcaopersonal.com#loja",
        "preco": "R$ 139,90",
        "custo_dia": "R$ 2,33 / dia",
        "cenario_nome": "Deck de Madeira à Beira-Mar com Pôr do Sol",
        "cenario_detalhe": "Deck de madeira rústica à beira-mar com o oceano calmo ao entardecer, céu em degradê dourado e azul profundo, brisa costeira fresca e atmosfera de longevidade e vigor.",
        "prompt_cenario_runpod": "Serene oceanfront wooden deck at golden hour sunset, calm blue sea waves, warm golden sun glow, pure fresh coastal atmosphere, cinematic vertical 9:16",
        "persona_tipo": "maduro_grisalho",
        "prompt_persona": "Handsome mature Brazilian man 60 years old with athletic posture and neat silver-grey hair, wearing casual navy polo shirt, looking outward at the sea with vitality, vitality and health longevity",
        "script": "A comida moderna é cheia de óleos inflamatórios que travam a sua recuperação. O ômega 3 ultra concentrado equilibra suas células, protege o coração, limpa os vasos e acaba com a rigidez articular matinal!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "INFLAMAÇÃO SILENCIOSA TRAVA O CORPO!", "color": "white", "size": 50},
            {"start": 4.7, "end": 9.8, "text": "EPA E DHA PUROS: SAÚDE DO CORAÇÃO E ARTICULAÇÃO!", "color": "gold", "size": 46},
            {"start": 9.9, "end": 15.2, "text": "LONGEVIDADE E VITALIDADE AOS 40+ E 60+!", "color": "white", "size": 48}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """🐟 A INFLAMAÇÃO SILENCIOSA QUE ESTÁ ACELERANDO O SEU ENVELHECIMENTO!

A alimentação moderna tem uma proporção desastrosa de 15:1 entre Ômega 6 (pró-inflamatório) e Ômega 3. Isso gera uma cascata inflamatória silenciosa no endotélio dos vasos sanguíneos, nas articulações e nas membranas celulares.

O Ômega 3 Ultra Concentrado em cápsulas com alta concentração de EPA e DHA age como um potente extintor de incêndio biológico:
❤️ Reduz triglicerídeos e protege a saúde cardiovascular
🧠 Estimula a função cognitiva e clareza mental
🦴 Desinflama cartilagens, reduzindo dores nas juntas

🔗 Suplementação certificada livre de metais pesados na Bio: marcaopersonal.com#loja

#marcao #omega3 #saude #longevidade #antiinflamatorio #coracao #vitalidade #saudecardiovascular"""
    },
    {
        "dia": 11,
        "id": "dia11_roupas_compressao_venosa",
        "titulo": "O Retorno Venoso e a Ciência do Tecido Dry-Fit UV50+",
        "categoria": "VESTUÁRIO DE ALTA PERFORMANCE",
        "produto": "Camiseta Térmica e Bermuda de Compressão UV50+",
        "link_venda": "https://marcaopersonal.com#loja",
        "preco": "R$ 69,90",
        "custo_dia": "R$ 0,38 / uso",
        "cenario_nome": "Parque Urbano com Trilha de Cascalho e Bosque de Árvores",
        "cenario_detalhe": "Parque urbano arborizado com túnel natural de árvores frondosas, trilha de cascalho fino sombreada, raios solares da manhã filtrados pelas copas, atmosfera de esporte e vitalidade.",
        "prompt_cenario_runpod": "Lush green urban running park with shaded gravel trail, morning sunlight filtering through tall green trees, fresh morning air, athletic outdoor environment, 8k vertical 9:16",
        "persona_tipo": "corredor_urbano",
        "prompt_persona": "Fit athletic Brazilian runner in sleek black compression thermal shirt and compression shorts with phone pocket, running in steady stride, defined muscles, professional athletic aesthetic",
        "script": "Roupa de compressão não é só visual fitness, é ciência do retorno venoso! Ela segura a vibração do músculo na passada pesada, evita assaduras entre as pernas e mantém a temperatura do corpo estável!",
        "subtitles": [
            {"start": 0.3, "end": 4.5, "text": "ROUPA DE COMPRESSÃO É BIOMECÂNICA!", "color": "white", "size": 52},
            {"start": 4.6, "end": 9.8, "text": "MELHORA O RETORNO VENOSO E A POTÊNCIA!", "color": "gold", "size": 48},
            {"start": 9.9, "end": 15.0, "text": "ZERO ASSADURAS E PROTEÇÃO UV50+!", "color": "white", "size": 50}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """🥋 POR QUE ATLETAS DE ELITE NUNCA MAIS TREINAM COM ROUPA COMUM?

A roupa de compressão graduada exerce pressão mecânica calculada sobre os compartimentos musculares. Isso aumenta a velocidade do fluxo sanguíneo nas veias profundas, acelerando a drenagem de lactato e a oxigenação dos tecidos.

Benefícios comprovados na prática:
🩸 Melhora do retorno venoso e menos inchaço nas pernas
🦵 Eliminação total de assaduras por atrito no agachamento e na corrida
☀️ Tecido inteligente com proteção UV50+ e tecnologia Dry-Fit térmica

🔗 Garanta suas peças oficiais na nossa vitrine: marcaopersonal.com#loja

#marcao #roupadecompressao #dryfit #treinodepernas #corrida #compressao #performance"""
    },
    {
        "dia": 12,
        "id": "dia12_gordura_visceral_infarto",
        "titulo": "A Gordura Oculta que Envolve o Coração e o Fígado",
        "categoria": "MÉTRICAS CLÍNICAS & RISCO CARDÍACO",
        "produto": "Balança Inteligente Shopee BIA (Rastreamento de Gordura Visceral)",
        "link_venda": "https://s.shopee.com.br/2BFoInIBeb",
        "preco": "R$ 34,90",
        "custo_dia": "R$ 0,09 / dia",
        "cenario_nome": "Laboratório de Biometria Esportiva com Telas 3D",
        "cenario_detalhe": "Laboratório moderno de biometria e cardiologia esportiva com iluminação azul ciano futurista, telas escuras com hologramas 3D de órgãos vitais e índices de adiposidade visceral.",
        "prompt_cenario_runpod": "High-tech sports science laboratory, dark background with glowing cyan and orange medical holographic diagrams of human internal organs and visceral fat levels, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina in modern black athletic gear, analyzing biological data on high-tech tablet screen, sharp intelligent expression, clinical precision",
        "script": "A gordura perigosa de verdade não é a que você aperta na pele com os dedos: é a gordura visceral que abraça o fígado e o coração! A nossa balança inteligente escaneia seu nível de risco em três segundos na Shopee!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "A GORDURA MAIS PERIGOSA ESTÁ ESCONDIDA!", "color": "white", "size": 48},
            {"start": 4.7, "end": 9.9, "text": "GORDURA VISCERAL ENVOLVE CORAÇÃO E FÍGADO!", "color": "gold", "size": 46},
            {"start": 10.0, "end": 15.4, "text": "ESCANEIE SEU NÍVEL COM A BALANÇA SHOPEE!", "color": "white", "size": 48}
        ],
        "template_hyperframes": "marcao_balanca_bioimpedancia",
        "caption": """⚠️ A GORDURA INVISÍVEL QUE COBRA UM PREÇO ALTO DA SUA SAÚDE!

Você sabia que existem dois tipos de gordura no corpo?
1️⃣ A gordura subcutânea (aquela mole que fica logo abaixo da pele).
2️⃣ A GORDURA VISCERAL: essa é a mais perigosa, pois fica alojada no interior da cavidade abdominal, envolvendo órgãos vitais como fígado, pâncreas e intestinos.

A gordura visceral libera citocinas inflamatórias direto na circulação porta, aumentando o risco de infarto, pressão alta e diabetes tipo 2.

Com a Balança Inteligente Shopee de Bioimpedância (R$ 34,90):
⚡ Os 4 eletrodos BIA medem a resistência elétrica tecidual e apontam o seu nível de gordura visceral de 1 a 12 instantaneamente.

🔗 Link oficial de fábrica na Shopee na Bio: marcaopersonal.com

#marcao #gorduravisceral #saude #bioimpedancia #coracao #prevencao #emagrecimento"""
    },
    {
        "dia": 13,
        "id": "dia13_manguito_rotador_supino",
        "titulo": "O Fim da Dor no Ombro ao Supinar: Blindagem do Manguito",
        "categoria": "REABILITAÇÃO & ESTABILIDADE ESCAPULAR",
        "produto": "Kit Faixas Elásticas para Manguito Rotador Shopee",
        "link_venda": "https://s.shopee.com.br/4Ve0NSPas4",
        "preco": "R$ 24,90",
        "custo_dia": "R$ 0,13 / dia",
        "cenario_nome": "Sala de Fisioterapia Esportiva com Espelhos e Faixas",
        "cenario_detalhe": "Sala ampla de fisioterapia esportiva e mobilidade com espelho panorâmico, faixas elásticas de tração coloridas fixadas na parede, piso limpo de madeira e halteres leves de aquecimento.",
        "prompt_cenario_runpod": "Clean bright sports physical therapy studio, wooden floors, wall-mounted resistance tubing, large mirror reflecting precision warm-up exercises, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina in black sleeveless gym shirt, performing standing external shoulder rotation with light resistance mini band, elbows pinned to sides, perfect rehab posture",
        "script": "Sentiu fisgada na frente do ombro na descida do supino? Cuidado com o manguito rotador! Três séries de rotação externa com faixa elástica antes de treinar peito lubrificam a articulação e acabam com a dor!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "FISGADA NO OMBRO AO SUPINAR?", "color": "white", "size": 52},
            {"start": 4.7, "end": 9.8, "text": "BLINDE O MANGUITO COM FAIXAS ELÁSTICAS!", "color": "gold", "size": 48},
            {"start": 9.9, "end": 15.0, "text": "KIT MANGUITO SHOPEE POR R$ 24,90!", "color": "white", "size": 50}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """💪 DOR NO OMBRO NO SUPINO? COMO SALVAR SEU MANGUITO ROTADOR!

O ombro é a articulação mais móvel e mais instável de todo o corpo humano. A cabeça do úmero é rasa e depende de 4 pequenos músculos para não sair do lugar: Supraespinhal, Infraespinhal, Redondo Menor e Subescapular (o Manguito Rotador).

Se você vai direto pro supino pesado com o ombro frio, o tendão do supraespinhal é esmagado contra o acrômio (síndrome do impacto).

Protocolo de 3 minutos antes do treino de peito:
1️⃣ Rotação externa na polia ou elástico leve (3x15 cada lado).
2️⃣ Rotação interna controlada.
3️⃣ Depressão escapular firme no banco.

🔗 Kit de Faixas de Manguito na Shopee por apenas R$ 24,90 na Bio: marcaopersonal.com

#marcao #ombro #manguitorotador #supino #prevencao #fisioterapiaesportiva #musculacao"""
    },
    {
        "dia": 14,
        "id": "dia14_hidratacao_densidade_celular",
        "titulo": "40ml de Água por Kg: O Eletrólito que Multiplica a Força",
        "categoria": "FISIOLOGIA CELULAR & HIDRATAÇÃO",
        "produto": "Balança Shopee (% Água Corporal) + Garrafa Térmica Motivacional",
        "link_venda": "https://s.shopee.com.br/2BFoInIBeb",
        "preco": "R$ 34,90",
        "custo_dia": "R$ 0,09 / dia",
        "cenario_nome": "Lounge Fitness Contemporâneo com Jardim Vertical",
        "cenario_detalhe": "Lounge fitness contemporâneo com parede verde natural de folhagens tropicais, bancos de madeira e iluminação zen suave, estação de hidratação moderna com água gelada.",
        "prompt_cenario_runpod": "Contemporary wellness fitness lounge, lush living green plant wall, natural wood seating, serene modern hydration station, ambient morning light, 8k vertical 9:16",
        "persona_tipo": "mulher_atletica",
        "prompt_persona": "Hydrated radiant athletic Brazilian woman in stylish fitness outfit, holding sleek matte black motivational water bottle, drinking fresh water with energetic satisfaction, healthy vitality",
        "script": "Sabia que perder só dois por cento de água corporal derruba sua força em quinze por cento no treino? Água transporta aminoácidos pras células e lubrifica os discos da coluna. Multiplique seu peso por quarenta!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "-2% DE ÁGUA = -15% DE FORÇA NO TREINO!", "color": "white", "size": 48},
            {"start": 4.7, "end": 9.8, "text": "40ML DE ÁGUA POR KG CORPORAL AO DIA!", "color": "gold", "size": 48},
            {"start": 9.9, "end": 15.0, "text": "MEÇA SUA HIDRATAÇÃO NA BALANÇA SHOPEE!", "color": "white", "size": 48}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """💧 DESIDRATADO NÃO CONSTRÓI MÚSCULO: A MATEMÁTICA DA ÁGUA!

70% do tecido muscular é pura água! Se o seu sarcoplasma estiver desidratado, a síntese proteica despenca e a viscosidade do sangue aumenta, sobrecarregando o coração.

A conta exata do Treinador Marcão:
Multiplique seu peso em kg por 40ml de água.
Exemplo: 75kg x 40 = 3.000ml (3 litros cravados ao longo do dia).

A Balança de Bioimpedância da Shopee (R$ 34,90) mede a % de água corporal real em cada pesagem para você nunca treinar desidratado.

🔗 Garanta sua balança no link da Bio: marcaopersonal.com

#marcao #hidratacao #agua #fisiologia #treino #saude #rendimento #bioimpedancia"""
    },
    {
        "dia": 15,
        "id": "dia15_vigor_masculino_circulacao",
        "titulo": "Vigor, Óxido Nítrico e Saúde Vascular Masculina 40+",
        "categoria": "SAÚDE MASCULINA & VIGOR 40+",
        "produto": "Caneta Peniana Azempika Original (Clinical Formula 20ml)",
        "link_venda": "https://ev.braip.com/ref?pl=plaljlxy&ck=che6vnvr&af=afine5z3yv",
        "preco": "R$ 99,00",
        "custo_dia": "R$ 3,30 / dia",
        "cenario_nome": "Gabinete Executivo Sofisticado com Estante de Mogno",
        "cenario_detalhe": "Gabinete executivo de alto padrão com estante de livros em mogno escuro, poltrona de couro marrom Chesterfield, iluminação indireta quente elegante, atmosfera de liderança e discrição.",
        "prompt_cenario_runpod": "High-end luxury executive private office, dark mahogany bookshelves, brown Chesterfield leather chair, warm subtle desk lamp lighting, distinguished masculine elegance, 8k vertical 9:16",
        "persona_tipo": "maduro_grisalho",
        "prompt_persona": "Distinguished handsome Brazilian mature gentleman 62 years old with neat grey silver hair, impeccable athletic posture in tailored dress shirt, confident self-assured gaze, masculine vitality",
        "script": "Aos quarenta e cinquenta anos a circulação periférica diminui e o óxido nítrico cai. Cuidar da saúde vascular íntima é essencial pra manter a firmeza, a confiança e a energia masculina no auge!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "SAÚDE VASCULAR MASCULINA APÓS OS 40!", "color": "white", "size": 48},
            {"start": 4.7, "end": 9.8, "text": "ÓXIDO NÍTRICO E CIRCULAÇÃO ÍNTIMA!", "color": "gold", "size": 48},
            {"start": 9.9, "end": 15.0, "text": "VITALIDADE E FIRMEZA NO LINK DA BIO!", "color": "white", "size": 50}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """🦁 VIGOR E SAÚDE VASCULAR MASCULINA 40+ E 50+: O QUE NINGUÉM TE CONTA!

Com o passar dos anos, a elasticidade endotelial dos vasos sanguíneos e a síntese de óxido nítrico sofrem uma queda natural. Isso afeta a microcirculação periférica, a oxigenação dos tecidos cavernosos e a confiança do homem maduro.

Cuidar da vascularização não é tabu: é ciência e longevidade masculina!

Pilares do vigor aos 40+:
1️⃣ Treinos de força multiarticulares (elevação natural de testosterona).
2️⃣ Vasodilatação tópica e circulatória com ativos bioestimulantes.
3️⃣ Sono profundo de 7 a 8 horas sem interrupções.

🔗 Fórmula clínica com envio 100% discreto no link da Bio: marcaopersonal.com

#marcao #saudemasculina #homemmaduro #vigor #circulacao #longevidade #vitalidade"""
    },
    {
        "dia": 16,
        "id": "dia16_calistenia_funcional_abdomen",
        "titulo": "Core de Aço e Abdômen Trincado Sem Aparelhos",
        "categoria": "CALISTENIA & CORE FUNCTIONAL",
        "produto": "Kit Treino Funcional em Casa Shopee (R$ 49,90)",
        "link_venda": "https://s.shopee.com.br/6fiUxRLoRK",
        "preco": "R$ 49,90",
        "custo_dia": "R$ 0,27 / dia",
        "cenario_nome": "Parque de Calistenia ao Ar Livre na Orla da Lagoa",
        "cenario_detalhe": "Parque de calistenia urbana à beira de lagoa serena, barras de ferro pretas fosco, piso de areia limpa, céu azul matinal com sol radiante, espaço ao ar livre dinâmico.",
        "prompt_cenario_runpod": "Outdoor calisthenics workout park near scenic lake at sunrise, black steel pull-up bars and dip stations, golden sunlight reflecting on water, 8k vertical 9:16",
        "persona_tipo": "corredor_urbano",
        "prompt_persona": "Athletic Brazilian man with sharp chiseled six-pack abs, hanging from pull-up bar performing controlled leg raises, intense core engagement, raw calisthenics strength",
        "script": "Fazer mil abdominais não vai queimar a sua barriga! O segredo de um abdômen de aço é fortalecer o transverso do abdômen com pranchas, calistenia e déficit calórico monitorado no aplicativo do Marcão!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "1000 ABDOMINAIS NÃO QUEIMAM BARRIGA!", "color": "white", "size": 48},
            {"start": 4.7, "end": 9.8, "text": "TRANSVERSO DO ABDÔMEN E CORE DE AÇO!", "color": "gold", "size": 48},
            {"start": 9.9, "end": 15.0, "text": "ACALME O METABOLISMO NO LINK DA BIO!", "color": "white", "size": 48}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """⚡ O MITO DOS 1000 ABDOMINAIS: O QUE REALMENTE TRINCA O CORE?

Não existe queima de gordura localizada: fazer 500 abdominais flexiona a coluna, mas não tira a capa de gordura que esconde os gomos do reto abdominal.

Como construir um abdômen de respeito:
🧱 Fortalecimento do Transverso do Abdômen com pranchas isométricas e vácuo estomacal.
🔥 Déficit Calórico Controlado (queimar mais calorias do que ingere).
🏋️ Exercícios compostos pesados (agachamento e terra exigem estabilização máxima do core).

🔗 Acesse a planilha completa de treino funcional em casa na Bio: marcaopersonal.com

#marcao #abdomen #core #calistenia #pranchaabdominal #barriganegativa #treinodecore"""
    },
    {
        "dia": 17,
        "id": "dia17_tmb_deficit_calorico",
        "titulo": "Por que Passar Fome Desacelera Seu Metabolismo (A TMB Real)",
        "categoria": "METABOLISMO & TERMODINÂMICA",
        "produto": "Balança Inteligente Shopee BIA (R$ 34,90)",
        "link_venda": "https://s.shopee.com.br/2BFoInIBeb",
        "preco": "R$ 34,90",
        "custo_dia": "R$ 0,09 / dia",
        "cenario_nome": "Consultório do Marcão Personal com Telas Gráficas 3D",
        "cenario_detalhe": "Consultório moderno com prancheta digital, gráficos metabólicos 3D na tela, janela com vista para cidade moderna, iluminação indireta executiva esportiva.",
        "prompt_cenario_runpod": "High-tech personal training consultation office, digital tablet displaying 3D metabolic charts, panoramic window overlooking skyline, clean athletic medical aesthetic, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina in sharp athletic trainer outfit, pointing at holographic metabolic energy chart on screen, authoritative trustworthy personal coach presence",
        "script": "Cortou toda a comida e parou de emagrecer? O seu corpo entrou em modo econômico! Para queimar gordura de verdade você precisa calcular sua Taxa Metabólica Basal real na balança inteligente!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "PASSAR FOME TRAVA SEU METABOLISMO!", "color": "white", "size": 50},
            {"start": 4.7, "end": 9.8, "text": "TERMOGÊNESE ADAPTATIVA E A TMB REAL!", "color": "gold", "size": 48},
            {"start": 9.9, "end": 15.0, "text": "CALCULE SUA TMB NA BALANÇA SHOPEE R$ 34,90!", "color": "white", "size": 46}
        ],
        "template_hyperframes": "marcao_balanca_bioimpedancia",
        "caption": """📉 POR QUE CORTAR COMIDA DEMAIS FAZ VOCÊ ENGORDAR DEPOIS?

Quando você entra em um déficit calórico extremo e passa fome, a tireoide reduz a conversão de T4 em T3 e o corpo diminui o gasto energético diário por termogênese adaptativa (modo de sobrevivência).

Resultado: você perde músculo, fica sem energia e acumula gordura no primeiro deslize.

O jeito certo e científico do Marcão:
1️⃣ Conheça a sua Taxa Metabólica Basal (TMB) exata na Balança Shopee BIA.
2️⃣ Crie um déficit moderado de apenas 400 a 500 kcal.
3️⃣ Mantenha a proteína alta (2g/kg) para preservar a massa magra.

🔗 Descubra sua TMB com a balança na Shopee por apenas R$ 34,90: marcaopersonal.com

#marcao #metabolismo #tmb #deficitcalorico #emagrecimento #dietasempassarfome #bioimpedancia"""
    },
    {
        "dia": 18,
        "id": "dia18_pre_treino_vasodilatacao",
        "titulo": "Cafeína, Beta-Alanina e Vasodilatação Sem Ansiedade",
        "categoria": "ENERGIA & FOCO NEURAL",
        "produto": "Pré-Treino Concentrado Oficial Marcão Personal",
        "link_venda": "https://marcaopersonal.com#loja",
        "preco": "R$ 119,90",
        "custo_dia": "R$ 3,99 / dose",
        "cenario_nome": "Vestiário VIP de Academia com Armários Pretos e Espelho LED",
        "cenario_detalhe": "Vestiário premium de clube esportivo com armários de aço preto fosco, piso de porcelanato escuro acetinado, iluminação embutida linear nos espelhos, ambiente de concentração.",
        "prompt_cenario_runpod": "Luxury modern gym locker room, dark charcoal matte lockers, backlit vertical mirrors, atmospheric focused preparation lighting, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina in black workout singlet, tying his training shoes on wooden bench with focused intensity, preparing for high-volume leg day",
        "script": "Cansado depois de um dia de trabalho e sem energia pra treinar? Um pré-treino bem formulado tampona o ácido lático com beta-alanina, abre seus vasos sanguíneos e liga seu foco no modo leão!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "SEM ENERGIA DEPOIS DO TRABALHO?", "color": "white", "size": 52},
            {"start": 4.7, "end": 9.8, "text": "BETA-ALANINA E FOCO NEURAL SEM ANSIEDADE!", "color": "gold", "size": 46},
            {"start": 9.9, "end": 15.0, "text": "LIGUE O MODO LEÃO NO LINK DA BIO!", "color": "white", "size": 52}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """⚡ CANSADO DO TRABALHO? COMO REATIVAR O FOCO PARA TREINAR PESADO!

A fadiga do final do dia é mais mental e neuromuscular do que muscular. A adenosina se acumula nos receptores cerebrais, criando a sensação de cansaço extremo.

A sinergia inteligente de nutrientes pré-treino:
🧠 Cafeína anidra pura: bloqueia os receptores de adenosina.
🧪 Beta-Alanina: eleva os níveis intramusculares de carnosina, tamponando os íons H+ e atrasando a queimação ácida do músculo.
🩸 Arginina e Citrulina: vasodilatação endotelial potente com mais oxigênio e pump muscular.

🔗 Conheça as opções recomendadas com laudo no link da Bio: marcaopersonal.com#loja

#marcao #pretreino #energia #foconoobjetivo #betaalanina #musculacao #treinointenso"""
    },
    {
        "dia": 19,
        "id": "dia19_falhas_capilares_biotina",
        "titulo": "Fortalecimento dos Fios e Absorção de Nutrientes na Raiz",
        "categoria": "ESTÉTICA CAPILAR & NUTRIÇÃO",
        "produto": "Kit IArmonize Capilar em 4 Fases (Homologado)",
        "link_venda": "https://marcaopersonal.com#loja",
        "preco": "R$ 189,90",
        "custo_dia": "R$ 3,16 / dia",
        "cenario_nome": "Banheiro de Mármore Branco Carrara Iluminado",
        "cenario_detalhe": "Banheiro de alto padrão com bancada de mármore branco Carrara, espelho com iluminação LED frontal sem sombras, frascos de cuidados estéticos minimalistas e toalhas pretas dobradas.",
        "prompt_cenario_runpod": "Luxury master bathroom, white Carrara marble walls and counters, bright even LED mirror vanity lighting, clean minimalist men's grooming setup, 8k vertical 9:16",
        "persona_tipo": "maduro_grisalho",
        "prompt_persona": "Distinguished fit mature Brazilian man 58 years old with neat salt-and-pepper hair, looking at his healthy hair density in illuminated mirror with satisfied confidence",
        "script": "Notou entradas aumentando ou cabelo afinando no banho? O estresse e o DHT fecham a raiz dos fios! A nutrição folicular estimula a microcirculação pra manter seus cabelos fortes e densos!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "ENTRADAS AUMENTANDO OU CABELO AFINANDO?", "color": "white", "size": 48},
            {"start": 4.7, "end": 9.8, "text": "ESTÍMULO DA MICROCIRCULAÇÃO FOLICULAR!", "color": "gold", "size": 48},
            {"start": 9.9, "end": 15.0, "text": "NUTRIÇÃO CAPILAR COMPLETA NA BIO!", "color": "white", "size": 50}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """💈 CABELOS AFINANDO OU FALHAS NO TOPO? ENTENDA O MOTIVO!

A queda capilar e o afinamento dos fios estão associados à miniaturização folicular provocada pelo excesso de DHT e à má irrigação sanguínea dos capilares do couro cabeludo.

Para reverter esse processo:
1️⃣ Estímulo vascular tópico para oxigenação da papila dérmica.
2️⃣ Biotina, Zinco e Vitaminas do Complexo B para síntese de queratina.
3️⃣ Controle do estresse e do cortisol diário.

🔗 Tratamento completo em 4 fases homologado no link da Bio: marcaopersonal.com#loja

#marcao #cabelo #quedadecabelo #saudecapilar #homemmaduro #esteticamasculina #biotina"""
    },
    {
        "dia": 20,
        "id": "dia20_cadencia_tempo_sob_tensao",
        "titulo": "Não Conte Repetições: Conte o Tempo Sob Tensão (TUT)",
        "categoria": "BIOMECÂNICA & HIPERTROFIA",
        "produto": "Ficha Personalizada do Aluno (Portal do Aluno Marcão)",
        "link_venda": "https://marcaopersonal.com/aluno",
        "preco": "Consultoria VIP",
        "custo_dia": "R$ 0,66 / dia",
        "cenario_nome": "Área de Peso Livre com Iluminação Dramática Chiaroscuro",
        "cenario_detalhe": "Área de pesos livres com contrastes dramáticos de luz e sombra, halteres monolíticos pretos, piso de alta absorção e espelhos fumê industriais.",
        "prompt_cenario_runpod": "Moody atmospheric bodybuilding free weights area, dramatic chiaroscuro high contrast lighting, black iron dumbbells, intense muscular focus, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina in black dry-fit shirt performing slow controlled preacher curl, veins mapped on forearms, intense 4-second eccentric tempo focus",
        "script": "Fazer dez repetições jogando o peso pra cima não constrói músculo! O que gera hipertrofia real é a fase excêntrica de três a quatro segundos. Controle a descida e sinta as fibras rasgando!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "NÃO CONTE APENAS REPETIÇÕES!", "color": "white", "size": 52},
            {"start": 4.7, "end": 9.8, "text": "TEMPO SOB TENSÃO: 3 A 4S NA DESCIDA!", "color": "gold", "size": 48},
            {"start": 9.9, "end": 15.0, "text": "MONTE SEU TREINO COM O MARCÃO NA BIO!", "color": "white", "size": 48}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """⏱️ VOCÊ ESTÁ ROUBANDO NO TREINO E NEM PERCEBEU!

Muitos praticantes pegam um peso que não aguentam, usam impulso do corpo e soltam a barra em 0.5 segundo. Isso é treino para o ego, não para o músculo!

A fase EXCÊNTRICA (quando o músculo se alonga sob carga) é a que causa o maior dano microscópico produtivo nas miofibrilas:
⏳ Segure a descida por 3 a 4 segundos controlados.
💥 Pressione na fase concêntrica com potência em 1 segundo.
🔥 Mantenha a série entre 40 e 50 segundos de Tensão Contínua (TUT).

🔗 Quer a sua ficha montada na medida certa com as cadências exatas? Acesse a plataforma no link da Bio: marcaopersonal.com

#marcao #hipertrofia #temposobtensao #musculacao #treinointenso #cadencia #tecnicadetreino"""
    },
    {
        "dia": 21,
        "id": "dia21_acucar_insulina_visceral",
        "titulo": "O Pico de Insulina e o Bloqueio da Queima de Gordura",
        "categoria": "ENDOCRINOLOGIA DO EMAGRECIMENTO",
        "produto": "Mentoria Nutricional Marcão (Visão de IA para Fotos de Comida)",
        "link_venda": "https://marcaopersonal.com",
        "preco": "Mentoria VIP",
        "custo_dia": "R$ 0,09 / dia (Balança)",
        "cenario_nome": "Cozinha com Potes Herméticos de Meal Prep Saudável",
        "cenario_detalhe": "Cozinha planejada clara e organizada, potes herméticos de vidro com refeições balanceadas (peito de frango grelhado, arroz integral e legumes verdes no vapor), prato saudável decorado.",
        "prompt_cenario_runpod": "Bright modern kitchen with organized glass meal prep containers filled with grilled chicken, broccoli, sweet potato, healthy lifestyle aesthetic, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina in casual athletic shirt, holding his phone over a healthy balanced chicken and rice meal, taking a photo for AI nutrition scanning, healthy life",
        "script": "Comeu doce ou pão refinado? O pico de insulina trava a queima de gordura por horas! Na nossa mentoria você tira foto do prato no WhatsApp e a inteligência artificial te dá o feedback na hora!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "PICO DE INSULINA TRAVA A QUEIMA DE GORDURA!", "color": "white", "size": 46},
            {"start": 4.7, "end": 9.8, "text": "FOTO DO PRATO COM FEEDBACK DE MACROS NA HORA!", "color": "gold", "size": 46},
            {"start": 9.9, "end": 15.0, "text": "ATATIVE SUA MENTORIA NO WHATSAPP!", "color": "white", "size": 50}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """🍽️ O QUE ACONTECE NO SEU CORPO QUANDO VOCÊ TEM UM PICO DE INSULINA?

A insulina é um hormônio altamente anabólico, mas ela funciona em mão única: quando seus níveis plasmáticos estão elevados pelo consumo de açúcares ou carboidratos refinados, a enzima Lipase Sensível a Hormônio (LSH) é desligada.

Isso significa que enquanto a insulina estiver alta, a lipólise (quebra de gordura) está TRAVADA no seu corpo.

A solução inteligente do Marcão:
🥗 Combine carboidratos complexos com fibras e proteínas magras.
📸 Envie uma foto do seu prato no WhatsApp para a IA do Marcão analisar seus macronutrientes antes da primeira garfada!

🔗 Tenha o Marcão no seu WhatsApp agora mesmo: marcaopersonal.com

#marcao #insulina #dieta #emagrecimento #nutricao #mealprep #macros #alimentacaosaudavel"""
    },
    {
        "dia": 22,
        "id": "dia22_cardio_pos_treino_glicogenio",
        "titulo": "Cardio Antes ou Depois da Musculação? A Bioquímica Exata",
        "categoria": "PERIODIZAÇÃO DE TREINAMENTO",
        "produto": "Smartwatch Strava + Bermuda de Compressão",
        "link_venda": "https://marcaopersonal.com#loja",
        "preco": "R$ 189,90",
        "custo_dia": "R$ 0,52 / dia",
        "cenario_nome": "Mezanino de Esteiras Tecnológicas com Vista Panorâmica",
        "cenario_detalhe": "Mezanino de academia com fileira de esteiras ergométricas profissionais de frente para uma parede de vidro com vista para o horizonte urbano iluminado ao entardecer.",
        "prompt_cenario_runpod": "High-end gym cardio mezzanine, line of state-of-the-art treadmills facing large glass window overlooking twilight city lights, clean energetic vibe, 8k vertical 9:16",
        "persona_tipo": "corredor_urbano",
        "prompt_persona": "Fit athletic Brazilian runner running at steady pace on high-tech treadmill, smart watch telemetry glowing on wrist, sweat on forehead, focused endurance stride",
        "script": "Faz meia hora de corrida antes de puxar ferro? Pare agora! A musculação consome seu glicogênio. Se você deixar o cardio pro final, seu corpo usa gordura estocada pra manter a esteira girando!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "CARDIO ANTES OU DEPOIS DA MUSCULAÇÃO?", "color": "white", "size": 48},
            {"start": 4.7, "end": 9.8, "text": "CARDIO NO FINAL QUEIMA GORDURA PURA!", "color": "gold", "size": 48},
            {"start": 9.9, "end": 15.0, "text": "MONITORE NO STRAVA DO TIME MARCÃO!", "color": "white", "size": 50}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """⚡ CARDIO ANTES OU DEPOIS DA MUSCULAÇÃO? A RESPOSTA CIENTÍFICA DEFINITIVA!

Se o seu objetivo principal é HIPERTROFIA ou DEFINIÇÃO MUSCULAR:
Faça sempre o cardio DEPOIS da musculação (ou em horários separados)!

Por quê?
1️⃣ A musculação exige ATP e glicogênio muscular para gerar torque máximo. Se você gastar suas reservas correndo antes, suas cargas no treino caem em 25%.
2️⃣ Ao terminar o treino com pesos, seus estoques de glicogênio já estão depletados. Quando você sobe na esteira para o cardio pós-treino, o organismo é obrigado a mobilizar os ácidos graxos do tecido adiposo como combustível imediato!

🔗 Conecte seu Strava à nossa plataforma oficial: marcaopersonal.com

#marcao #cardio #musculacao #treino #emagrecimento #periodizacao #strava #queimadegordura"""
    },
    {
        "dia": 23,
        "id": "dia23_panturrilha_segundo_coracao",
        "titulo": "O Segundo Coração do Corpo: A Bomba Sanguínea Sóleo",
        "categoria": "CIRCULAÇÃO & MEMBROS INFERIORES",
        "produto": "Joelheira e Meias de Compressão Graduada Shopee",
        "link_venda": "https://s.shopee.com.br/AUvD3t2pKw",
        "preco": "R$ 29,90",
        "custo_dia": "R$ 0,16 / dia",
        "cenario_nome": "Escadaria Monumental de Concreto Arquitetônico ao Ar Livre",
        "cenario_detalhe": "Escadaria urbana monumental de concreto com degraus largos em parque público, cercada por gramados verdes sob céu matinal azul, local perfeito para treino pliométrico.",
        "prompt_cenario_runpod": "Monumental architectural concrete outdoor park staircase, morning clean daylight, surrounded by fresh green grass, powerful athletic training spot, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina in black compression running gear, doing dynamic calf raises on edge of concrete steps, deeply sculpted calves and Achilles tendon, athletic determination",
        "script": "Pula o treino de panturrilha porque acha difícil de crescer? A panturrilha é o segundo coração do corpo! A contração do músculo sóleo bombeia o sangue de volta pra cima e previne varizes e cansaço nas pernas!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "PANTURRILHA: O SEGUNDO CORAÇÃO DO CORPO!", "color": "white", "size": 48},
            {"start": 4.7, "end": 9.8, "text": "O MÚSCULO SÓLEO BOMBEIA O SANGUE PRA CIMA!", "color": "gold", "size": 46},
            {"start": 9.9, "end": 15.0, "text": "TREINE PANTURRILHAS COM AMPLITUDE MÁXIMA!", "color": "white", "size": 48}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """🩸 POR QUE A PANTURRILHA É CHAMADA DE O SEGUNDO CORAÇÃO DO CORPO?

A gravidade empurra o sangue para baixo o tempo todo. As veias das pernas possuem válvulas unidirecionais, mas dependem da compressão vigorosa dos músculos gastrocnêmio e sóleo para bombear o sangue venoso de volta ao coração.

Quando você treina panturrilhas com amplitude máxima:
✅ Melhora a circulação venosa e elimina a sensação de pernas pesadas.
✅ Previne varizes e tromboses.
✅ Aumenta a estabilidade do tornozelo para agachar sem desequilíbrio.

Dica de ouro: segure 2 segundos no ponto mais alto da contração e desça alongando completamente o calcanhar!

🔗 Itens de compressão circulatória homologados na Bio: marcaopersonal.com#loja

#marcao #panturrilha #circulacao #retornovenoso #treinodepernas #saude #musculacao"""
    },
    {
        "dia": 24,
        "id": "dia24_suplementacao_pos_40",
        "titulo": "A Virada dos 40 Anos: Como Blindar Músculos e Articulações",
        "categoria": "LONGEVIDADE & TESTOSTERONA 40+",
        "produto": "Kit Longevidade (Creatina Micronizada + Colágeno + Ômega 3)",
        "link_venda": "https://marcaopersonal.com#loja",
        "preco": "R$ 299,90",
        "custo_dia": "R$ 4,99 / dia",
        "cenario_nome": "Trilha de Montanha com Rochas e Vista Panorâmica",
        "cenario_detalhe": "Trilha em crista de montanha com afloramentos rochosos e vegetação nativa, vista panorâmica espetacular de vales ao entardecer dourado, ar puro e altitude.",
        "prompt_cenario_runpod": "Dramatic mountain summit hiking trail at golden hour, weathered rocks, panoramic mountain ridge view under warm golden sunlight, raw majestic nature, 8k vertical 9:16",
        "persona_tipo": "maduro_grisalho",
        "prompt_persona": "Strong fit mature Brazilian gentleman 58 years old with neat grey silver hair, wearing dark outdoor athletic jacket, standing tall on mountain overlook, healthy masculine vigor and vitality",
        "script": "Passou dos quarenta anos e acha que o shape é coisa do passado? Mentira! Com musculação pesada, creatina e colágeno você freia a sarcopenia e chega aos sessenta anos mais forte do que aos trinta!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "PASSOU DOS 40? O SHAPE NÃO É DO PASSADO!", "color": "white", "size": 48},
            {"start": 4.7, "end": 9.8, "text": "COMBATA A SARCOPENIA COM FORÇA E CIÊNCIA!", "color": "gold", "size": 46},
            {"start": 9.9, "end": 15.0, "text": "LONGEVIDADE E MÚSCULO FORTE NA BIO!", "color": "white", "size": 50}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """🦁 A VIRADA DOS 40 ANOS: COMO MANTER O MÚSCULO E A VITALIDADE NO AUGE!

A partir dos 35 anos, o corpo perde cerca de 1% a 2% de massa muscular ao ano por sarcopenia natural se você não fizer treinos de sobrecarga progressiva.

Mas isso não é destino: é escolha!

O trio de ouro da longevidade ativa:
1️⃣ Creatina Micronizada: preserva a força muscular e a função cognitiva cerebral.
2️⃣ Colágeno com Ácido Hialurônico: blinda as articulações contra o desgaste da cartilagem.
3️⃣ Ômega 3 EPA/DHA: combate a inflamação sistêmica e protege o coração.

🔗 Monte seu plano de longevidade com a equipe Marcão no link da Bio: marcaopersonal.com

#marcao #quarentao #cinquentao #longevidade #homemmaduro #saude #musculacao40mais #vitalidade"""
    },
    {
        "dia": 25,
        "id": "dia25_falso_magro_recomposicao",
        "titulo": "O Dilema do Falso Magro: Secar a Barriga ou Ganhar Massa?",
        "categoria": "RECOMPOSIÇÃO CORPORAL",
        "produto": "Balança Shopee BIA R$ 34,90 (Diagnóstico de Recomposição)",
        "link_venda": "https://s.shopee.com.br/2BFoInIBeb",
        "preco": "R$ 34,90",
        "custo_dia": "R$ 0,09 / dia",
        "cenario_nome": "Sala Privativa de Avaliação Física Esportiva",
        "cenario_detalhe": "Sala moderna de avaliação física com espelho quadriculado de simetria postural, iluminação clínica suave e balança de bioimpedância de aço inox no chão.",
        "prompt_cenario_runpod": "Clean private sports physique assessment studio, posture grid mirror wall, soft professional studio lighting, high precision scale on floor, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina in athletic coaching shirt, showing body recomposition metrics comparison on tablet, confident mentor expression, educational clarity",
        "script": "Braço fino mas com barriga estufada? Você é um falso magro! Não faça dieta de passar fome, senão você só vai virar um esqueleto flácido. O segredo é recomposição corporal com proteína alta e treino pesado!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "BRAÇO FINO E BARRIGA ESTUFADA?", "color": "white", "size": 52},
            {"start": 4.7, "end": 9.8, "text": "RECOMPOSIÇÃO CORPORAL: MASSA SOBE, GORDURA DESCE!", "color": "gold", "size": 46},
            {"start": 9.9, "end": 15.0, "text": "AVALIE SUA COMPOSIÇÃO NA BALANÇA SHOPEE!", "color": "white", "size": 46}
        ],
        "template_hyperframes": "marcao_balanca_bioimpedancia",
        "caption": """🎯 O DILEMA DO FALSO MAGRO: POR QUE SECAR PRIMEIRO É UM ERRO?

O "falso magro" tem pouquíssima massa muscular estrutural e um acúmulo desproporcional de gordura visceral e subcutânea no abdômen.

Se você fizer um cutting agressivo (cortar calorias demais), seu corpo queima a pouca massa magra que você tem, seu metabolismo cai e você continua flácido e com barriga!

A estratégia comprovada de Recomposição Corporal:
🥩 Mantenha as calorias na taxa de manutenção diária com proteína alta (2.2g/kg).
🏋️ Treine pesado buscando progressão de carga nos exercícios básicos.
⚖️ Monitore os 13 biomarcadores na Balança Inteligente da Shopee para acompanhar o ganho muscular real.

🔗 Balança oficial de R$ 34,90 na Bio: marcaopersonal.com

#marcao #falsomagro #recomposicaocorporal #emagrecimento #massamagra #treinopesado #dieta"""
    },
    {
        "dia": 26,
        "id": "dia26_dorsal_costas_em_v",
        "titulo": "Costas em V: A Amplitude das Escápulas e Ativação Dorsal",
        "categoria": "SIMETRIA ESTÉTICA & DORSAIS",
        "produto": "Straps de Algodão Shopee + Barra Fixa",
        "link_venda": "https://s.shopee.com.br/2BG5b2xhm2",
        "preco": "R$ 19,90",
        "custo_dia": "R$ 0,11 / dia",
        "cenario_nome": "Área de Barras Fixas e Força ao Ar Livre",
        "cenario_detalhe": "Área rústica de cross-training e calistenia ao ar livre com barras de ferro montadas em toras de madeira rústica, piso de terra compactada com cascalho, fim de tarde ensolarado.",
        "prompt_cenario_runpod": "Outdoor raw calisthenics pull-up rig, heavy industrial steel bars on rustic timber posts, late afternoon sunbeams through dust, raw strength atmosphere, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina viewed from behind performing wide grip overhand pull-up, chiseled wide V-taper back muscles flexing with incredible definition, athletic power",
        "script": "Quer afinar visualmente a cintura? Construa costas largas em V! A pegada pronada com puxada pelos cotovelos esmaga o grande dorsal e dá aquela silhueta atlética e imponente de verdade!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "QUER AFINAR A CINTURA? ALARGUE AS COSTAS!", "color": "white", "size": 48},
            {"start": 4.7, "end": 9.8, "text": "PUXE COM OS COTOVELOS: ATIVAÇÃO DORSAL MÁXIMA!", "color": "gold", "size": 46},
            {"start": 9.9, "end": 15.0, "text": "STRAP OFICIAL DE R$ 19,90 NA SHOPEE!", "color": "white", "size": 50}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """🦁 COSTAS LARGAS CRIAM A ILUSÃO DE CINTURA FINA: O EFEITO V-TAPER!

Na estética corporal clássica, o que cria a silhueta atlética não é apenas secar o abdômen, mas expandir a largura das escápulas e do latíssimo do dorso. Isso cria a famosa proporção V-Taper (ombros e costas largos descendo para uma cintura estreita).

O maior erro na puxada:
Puxar a barra com a força dos bíceps e antebraços.
O jeito certo do Marcão:
Pense nas suas mãos apenas como ganchos (use o strap de algodão para travar) e conduza a barra trazendo os COTOVELOS em direção aos bolsos da calça, esmagando as escápulas embaixo por 1 segundo!

🔗 Strap de Algodão Reforçado na Shopee por apenas R$ 19,90 no link da Bio: marcaopersonal.com

#marcao #dorsal #costasemv #vtaper #treinodecostas #barrafixa #musculacao #shopee"""
    },
    {
        "dia": 27,
        "id": "dia27_dor_tardia_antiinflamatorio",
        "titulo": "Tomar Remédio Pra Dor Muscular Anula Seu Treino!",
        "categoria": "FARMACOLOGIA ESPORTIVA & RECUPERAÇÃO",
        "produto": "Creatina Micronizada 100% Pura Nature's Prime",
        "link_venda": "https://ev.braip.com/ref?pl=pla1x6xn&ck=chen80rq&af=afimeno621",
        "preco": "R$ 169,90",
        "custo_dia": "R$ 1,68 / dia",
        "cenario_nome": "Sala de Descanso e Liberação Miofascial com Tatame",
        "cenario_detalhe": "Sala de relaxamento muscular e mobilidade com tatame cinza escuro, rolo de liberação miofascial preto de textura profunda, luz azul suave indireta, clima de recuperação celular.",
        "prompt_cenario_runpod": "Clean modern athletic recovery studio, dark grey floor mats, deep tissue foam roller, soft cool blue ambient mood lighting, recovery room, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina in comfortable black training attire, sitting on recovery mat stretching his hamstrings and drinking water, relaxed athletic recovery",
        "script": "Sentiu dor muscular pós-treino e tomou anti-inflamatório de farmácia? Pare já! O remédio bloqueia a enzima COX-2 e desliga a resposta inflamatória necessária pra reconstruir o músculo!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "TOMOU ANTI-INFLAMATÓRIO PÓS-TREINO?", "color": "white", "size": 50},
            {"start": 4.7, "end": 9.8, "text": "O REMÉDIO ANULA O SEU GANHO MUSCULAR!", "color": "gold", "size": 48},
            {"start": 9.9, "end": 15.0, "text": "RECUPERE COM ÁGUA E CREATINA PURA!", "color": "white", "size": 50}
        ],
        "template_hyperframes": "marcao_myth_buster",
        "caption": """🛑 O REMÉDIO QUE ESTÁ DELETANDO OS RESULTADOS DO SEU TREINO!

Sentiu aquela dor muscular boa no dia seguinte do treino de pernas e tomou um anti-inflamatório (como ibuprofeno ou diclofenaco) pra aliviar?

Você acabou de jogar sua sessão de treino no lixo!

Por que o anti-inflamatório anula a hipertrofia:
A inflamação muscular aguda pós-treino é um processo biológico mandatório: ela atrai as células satélites através da via das prostaglandinas (catalisadas pela enzima COX-2) para regenerar e hipertrofiar as fibras danificadas.

Quando o remédio bloqueia a dor, ele bloqueia também o sinal de crescimento!

O que fazer para recuperar com saúde:
💧 Beba 40ml/kg de água.
🧂 Creatina Micronizada Pura (R$ 1,68/dia).
😴 Sono profundo e mobilidade leve.

🔗 Creatina Oficial com selo de pureza na Bio: marcaopersonal.com

#marcao #dorpostreino #antiinflamatorio #hipertrofia #recuperacaomuscular #creatina #ciencia"""
    },
    {
        "dia": 28,
        "id": "dia28_treino_pernas_testosterona",
        "titulo": "O Dia de Perna Não É Opcional: O Choque Anabólico Global",
        "categoria": "FORÇA PESADA & IMPACTO HORMONAL",
        "produto": "Cinto de Musculação + Joelheira Neoprene Shopee",
        "link_venda": "https://s.shopee.com.br/4fxQZlKctc",
        "preco": "R$ 49,90",
        "custo_dia": "R$ 0,27 / dia",
        "cenario_nome": "Área de Leg Press 45° Articulado em Academia Industrial",
        "cenario_detalhe": "Academia estilo industrial com paredes de concreto escuro e tijolo aparente, máquina de Leg Press 45° de aço maciço carregada com anilhas pretas pesadas, luz lateral rasante.",
        "prompt_cenario_runpod": "Industrial heavy strength gym, heavy-duty 45 degree leg press machine loaded with heavy plates, exposed brick and dark concrete walls, dramatic athletic lighting, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina seated in 45-degree leg press with knee sleeves and weightlifting belt, powerful quadriceps muscles flexed in controlled pressing motion, intense gritty focus",
        "script": "Pular treino de perna porque dá preguiça? Nem pensar, meu parceiro! As pernas concentram mais de cinquenta por cento da sua massa muscular. Treinar perna pesada libera testosterona pro corpo todo!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "PULAR TREINO DE PERNAS? NEM PENSAR!", "color": "white", "size": 52},
            {"start": 4.7, "end": 9.8, "text": "50% DO SEU MÚSCULO ESTÁ NAS PERNAS!", "color": "gold", "size": 48},
            {"start": 9.9, "end": 15.0, "text": "CINTO E JOELHEIRA OFICIAIS NA SHOPEE!", "color": "white", "size": 48}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """🦵 DIA DE PERNA NÃO É OPCIONAL: É O MOTOR DO SEU METABOLISMO!

Você quer braços grandes, peitoral cheio e queima contínua de gordura, mas pula o treino de perna toda semana?

Os quadríceps, isquiotibiais e glúteos formam o maior complexo muscular do organismo humano:
🔥 Treinar perna queima o dobro de calorias por hora de qualquer treino de superiores.
⚡ O estresse sistêmico induz liberação acentuada de testosterona e GH na corrente sanguínea.
🛡️ Fortalece a pelve e protege sua lombar para o resto da vida!

Equipamentos obrigatórios para agachar pesado com segurança:
✅ Cinto Lombar Reforçado (R$ 49,90 na Shopee)
✅ Joelheira Neoprene 7mm (R$ 29,90 na Shopee)

🔗 Links oficiais de fábrica na Bio: marcaopersonal.com

#marcao #legday #treinodepernas #agachamento #testosterona #legpress #musculacao"""
    },
    {
        "dia": 29,
        "id": "dia29_acessorios_biomecanica",
        "titulo": "Acessórios Não São Enfeite: A Biomecânica que Salva Articulações",
        "categoria": "EQUIPAMENTOS & PERFORMANCE PROFISSIONAL",
        "produto": "Arsenal de Acessórios Oficiais Marcão Personal Shopee",
        "link_venda": "https://marcaopersonal.com#loja",
        "preco": "A partir de R$ 19,00",
        "custo_dia": "R$ 0,11 / dia",
        "cenario_nome": "Bancada Rústica de Oficina Esportiva com Equipamentos",
        "cenario_detalhe": "Bancada de preparação esportiva em madeira de lei escura com iluminação rasante, cinto lombar de couro preto, straps de algodão reforçados e joelheiras de neoprene organizadas em destaque.",
        "prompt_cenario_runpod": "High-end rustic wood athletic gear preparation table, sleek black leather weight belt, heavy-duty straps and neoprene sleeves cleanly displayed, warm dramatic studio lighting, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina inspecting professional gym accessories on the table, picking up heavy lifting straps, authoritative gym founder expertise, authentic sports craftsmanship",
        "script": "Cinto lombar, joelheira e straps não são enfeite de blogueiro: são ferramentas de biomecânica que blindam suas juntas e te deixam colocar mais carga sem arrebentar a coluna e os tendões!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "ACESSÓRIOS NÃO SÃO ENFEITE DE BLOGUEIRO!", "color": "white", "size": 48},
            {"start": 4.7, "end": 9.8, "text": "BIOMECÂNICA QUE SALVA SUAS JUNTAS E COLUNA!", "color": "gold", "size": 46},
            {"start": 9.9, "end": 15.0, "text": "EQUIPAMENTOS OFICIAIS MARCÃO NA SHOPEE!", "color": "white", "size": 48}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """⚙️ POR QUE ATLETAS SÉRIOS NÃO TREINAM SEM SEU ARSENAL DE PROTEÇÃO?

Musculação não é sobre quem aguenta a dor da lesão: é sobre CONSTÂNCIA por anos a fio sem precisar parar por cirurgia ou tendinite.

Os acessórios certos mudam seu jogo:
🔒 Cinto Lombar: estabiliza a coluna com pressão intra-abdominal.
🛡️ Joelheira Neoprene: retém calor e dissipa o impacto no tendão patelar.
🦁 Straps: tiram a sobrecarga do antebraço para focar 100% nas costas.

A melhor parte? Preço direto de fábrica na nossa loja oficial da Shopee com cupons de frete grátis!

🔗 Conheça todo o arsenal na Bio: marcaopersonal.com

#marcao #biomecanica #acessoriosfitness #treinopesado #cinturãolombar #straps #shopee"""
    },
    {
        "dia": 30,
        "id": "dia30_foco_mental_disciplina",
        "titulo": "O Cérebro Desiste Antes do Músculo: A Neurociência da Última Repetição",
        "categoria": "MENTALIDADE & PSICOLOGIA DO ESPORTE",
        "produto": "Protocolo de Mentoria VIP Marcão Personal no WhatsApp",
        "link_venda": "https://marcaopersonal.com",
        "preco": "R$ 19,90 / mês",
        "custo_dia": "R$ 0,66 / dia",
        "cenario_nome": "Mirante Panorâmico no Topo da Cidade no Pôr do Sol Dourado",
        "cenario_detalhe": "Mirante no topo de uma montanha ou arranha-céu com vista panorâmica de 360 graus da cidade sob um pôr do sol espetacular em tons dourados e violeta (golden hour), vento suave e horizonte infinito.",
        "prompt_cenario_runpod": "Breathtaking panoramic rooftop city overlook at golden hour sunset, endless skyline bathed in warm orange and purple hues, inspiring victorious atmosphere, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina in sleek black athletic apparel standing at the scenic overlook looking outward at the sunset horizon, victorious confident posture, inspirational resilience",
        "script": "Quando a série começa a queimar e sua mente manda parar, lembre-se: seu músculo ainda tem trinta por cento de energia de reserva! É nas duas últimas repetições que a disciplina separa o campeão do medíocre!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "O CÉREBRO DESISTE ANTES DO MÚSCULO!", "color": "white", "size": 52},
            {"start": 4.7, "end": 9.8, "text": "É NAS ÚLTIMAS DUAS REPETIÇÕES QUE O SHAPE MUDA!", "color": "gold", "size": 46},
            {"start": 9.9, "end": 15.0, "text": "NUNCA DESISTA DE VOCÊ! VEM PRO TIME MARCÃO!", "color": "white", "size": 48}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """🧠 A NEUROCIÊNCIA DA ÚLTIMA REPETIÇÃO: POR QUE A DISCIPLINA VENCE O TALENTO!

O cérebro humano é programado evolutivamente para economizar energia e fugir do desconforto físico. Quando a acidez láctica começa a arder na 8ª repetição, o sistema nervoso central dispara sinais de pânico mandando você soltar o peso.

Mas a ciência do exercício comprovou: nesse exato momento, suas fibras ainda têm pelo menos 30% de capacidade contrátil de reserva!

As repetições efetivas (aquelas 2 ou 3 próximas da falha concêntrica) são responsáveis por mais de 70% do estímulo anabólico de hipertrofia de todo o treino.

Vença a sua mente. Beba sua água. Cumpra o seu plano!

🔗 Venha treinar com o suporte diário do Marcão: marcaopersonal.com

#marcao #mindset #disciplina #foco #motivação #treinopesado #resiliencia #superacao"""
    },
    {
        "dia": 31,
        "id": "dia31_ranking_leao_campeoes",
        "titulo": "A Tribo dos Leões: O Orgulho da Consistência e do Pódio Top 5",
        "categoria": "COMUNIDADE & RANKING DOS CAMPEÕES",
        "produto": "Portal do Aluno Marcão Personal (`aluno.html`)",
        "link_venda": "https://marcaopersonal.com/aluno",
        "preco": "Incluso na Balança Shopee",
        "custo_dia": "R$ 0,09 / dia",
        "cenario_nome": "Pódio de Academia de Elite com Iluminação Ciano e Dourada",
        "cenario_detalhe": "Pódio atlético iluminado em estúdio contemporâneo com luzes neon ciano e dourada, troféu simbólico do Leão Alfa em pedestal de aço escovado, telas com o ranking Top 5 dos alunos mais dedicados.",
        "prompt_cenario_runpod": "Futuristic sports championship podium, glowing gold and cyan neon lights, brushed steel pedestal with lion emblem, digital holographic leaderboard in background, 8k vertical 9:16",
        "persona_tipo": "evandro",
        "prompt_persona": "Athletic fitness founder Evandro Gallina standing proudly next to the championship leaderboard podium, wearing executive athletic black polo, welcoming new champions with strong handshake and warm smile",
        "script": "Na nossa comunidade você não treina sozinho! Todo domingo o Marcão atualiza o ranking dos cinco alunos mais dedicados da semana que salvaram seus treinos e bateram suas metas. Venha fazer parte da Tribo dos Leões!",
        "subtitles": [
            {"start": 0.3, "end": 4.6, "text": "NA NOSSA TRIBO VOCÊ NUNCA TREINA SOZINHO!", "color": "white", "size": 48},
            {"start": 4.7, "end": 9.8, "text": "PÓDIO TOP 5 DOS LEÕES DA SEMANA!", "color": "gold", "size": 50},
            {"start": 9.9, "end": 15.0, "text": "ACESSE SEU PORTAL NO LINK DA BIO!", "color": "white", "size": 50}
        ],
        "template_hyperframes": "marcao_kinetic_hook",
        "caption": """🏆 O ORGULHO DA CONSISTÊNCIA: A TRIBO DOS LEÕES DO MARCÃO PERSONAL!

Treinar sozinho é fácil desistir na segunda semana. Mas quando você faz parte de um ecossistema com acompanhamento diário, metas na ponta do lápis e um ranking semanal dinâmico que celebra quem não falha, a sua disciplina atinge outro nível!

No nosso portal do aluno:
📊 Sua matemática física calibrada (água, calorias e proteína).
🏋️ Ficha dinâmica que você salva seu treino com 1 clique para acumular streak.
👑 Ranking Top 5 semanal dos alunos mais dedicados da semana!

Quem garante a Balança Shopee por R$ 34,90 destrava o acesso completo e o suporte no WhatsApp!

🔗 Acesse seu portal ou garanta sua balança no link da Bio: marcaopersonal.com

#marcao #tribodosleoes #ranking #alunotop #consistencia #disciplina #comunidadefitness #shape"""
    }
]


def obter_tema_do_dia(dia: int = None) -> dict:
    """Retorna o tema e cenário oficial para o dia informado (1 a 31)."""
    if dia is None:
        dia = datetime.now().day
    dia_idx = max(1, min(31, int(dia))) - 1
    return MATRIZ_31_DIAS[dia_idx]


def total_temas() -> int:
    return len(MATRIZ_31_DIAS)
