"""Categories, templates and reproducible examples; no stored results."""
CATEGORIES = [{'id': 'channels',
  'title': {'en': 'Radio channels', 'es': 'Canales de radio', 'fr': 'Canaux radio', 'de': 'Funkkanäle'},
  'description': {'en': 'Assign one of two channels to every transmitter (a device that emits radio signals), reducing '
                        'interference between devices sharing a channel.',
                  'es': 'Asigna uno de dos canales a cada transmisor (aparato que emite señales de radio), reduciendo las '
                        'interferencias entre los que comparten canal.',
                  'fr': 'Attribuez un des deux canaux à chaque émetteur (appareil qui émet des signaux radio) pour réduire les '
                        'interférences entre appareils sur le même canal.',
                  'de': 'Weisen Sie jedem Sender (einem Gerät, das Funksignale sendet) einen von zwei Kanälen zu, um Störungen '
                        'auf demselben Kanal zu verringern.'},
  'help': {'en': 'Own data: weights is a square table for 2–128 transmitters. Row and column numbers identify devices. Values '
                 'are nonnegative interference costs; the diagonal is zero and opposite entries must match. Only two channels; '
                 'no coverage or power constraints. For a generated test instead, use size (4–2048) and seed (0–2147483647); do '
                 'not include weights.',
           'es': 'Datos propios: weights es una tabla cuadrada para 2–128 transmisores. Cada fila y columna identifica un '
                 'aparato. Los números son costes de interferencia no negativos; la diagonal es cero y los valores opuestos '
                 'deben coincidir. Solo dos canales, sin restricciones de cobertura ni potencia. Para generar una prueba usa '
                 'size (4–2048) y seed (0–2147483647), sin weights.',
           'fr': 'Données propres : weights est un tableau carré pour 2–128 émetteurs, avec coûts positifs ou nuls, diagonale '
                 'nulle et valeurs symétriques. Deux canaux seulement, sans contraintes de couverture ni de puissance. Pour une '
                 'simulation, utilisez size (4–2048) et seed (0–2147483647), sans weights.',
           'de': 'Eigene Daten: weights ist eine quadratische Tabelle für 2–128 Sender. Nichtnegative Störkosten, Nullen auf der '
                 'Diagonale und symmetrische Werte. Nur zwei Kanäle, ohne Abdeckungs- oder Leistungsregeln. Für Testdaten: size '
                 '(4–2048) und seed (0–2147483647), ohne weights.'},
  'template': {'kind': 'channels', 'weights': [[0, 10, 8, 1], [10, 0, 1, 7], [8, 1, 0, 6], [1, 7, 6, 0]]},
  'synthetic': {'kind': 'channels', 'size': 1500, 'seed': 123}},
 {'id': 'partition',
  'title': {'en': 'Balance tasks', 'es': 'Reparto de tareas', 'fr': 'Répartir les tâches', 'de': 'Aufgaben verteilen'},
  'description': {'en': 'Split tasks between two teams, balancing workload and reducing competition for shared resources.',
                  'es': 'Reparte tareas entre dos equipos: equilibra la carga y reduce la competencia por recursos compartidos.',
                  'fr': 'Répartissez les tâches entre deux équipes : équilibrez la charge et réduisez la concurrence pour les '
                        'ressources.',
                  'de': 'Verteile Aufgaben auf zwei Teams: gleiche Lasten aus und verringere Konflikte um gemeinsame '
                        'Ressourcen.'},
  'help': {'en': 'durations contains the duration or workload of each task, in the same unit. Between 2 and 128 strictly '
                 'positive numbers. The answer gives the task numbers assigned to each group. This model has two identical '
                 'teams; it does not include deadlines or worker skills. For a generated large test, use Generate test data: '
                 'size 4–4096 and seed 0–2147483647. Keep the indicated variant; omit actual-data arrays. Generated tests use '
                 'the large model described in the examples, not the small template model.',
           'es': 'durations contiene la duración o carga de cada tarea, todas en la misma unidad. Entre 2 y 128 números mayores '
                 'que cero. La respuesta indica los números de tarea de cada grupo. El modelo usa dos equipos equivalentes; no '
                 'admite fechas límite ni habilidades de trabajadores. Para una prueba grande, pulsa Generar datos de prueba: '
                 'size 4–4096 y seed 0–2147483647. Mantén variant y no añadas tablas propias. La prueba generada usa el modelo '
                 'grande explicado en los ejemplos; la plantilla pequeña conserva el modelo descrito aquí.',
           'fr': 'durations contient la durée ou charge de chaque tâche dans une même unité : 2 à 128 nombres strictement '
                 'positifs. La réponse donne les numéros des tâches de chaque groupe. Deux équipes équivalentes, sans échéances '
                 'ni compétences. Pour un grand test : Générer des données, size 4–4096 et seed 0–2147483647. Conservez variant, '
                 'sans tableaux de données propres. Le modèle généré est celui des exemples ; le petit modèle est décrit ici.',
           'de': 'durations enthält die Dauer oder Last jeder Aufgabe in derselben Einheit: 2–128 positive Zahlen. Die Antwort '
                 'nennt die Aufgabennummern pro Gruppe. Zwei gleichwertige Teams, ohne Fristen oder Qualifikationen. Für große '
                 'Testdaten: Testdaten erzeugen, size 4–4096 und seed 0–2147483647. variant beibehalten, keine eigenen '
                 'Datentabellen ergänzen. Generierte Tests verwenden das Beispielmodell; die kleine Vorlage das hier '
                 'beschriebene Modell.'},
  'template': {'kind': 'partition', 'durations': [40, 30, 25, 20, 15, 10]},
  'own_description': {'en': 'Divide tasks between two teams or machines so their total workloads are as similar as possible. '
                            'Each task belongs to exactly one group.',
                      'es': 'Reparte tareas entre dos equipos o máquinas para que sus cargas totales sean lo más parecidas '
                            'posible. Cada tarea se asigna a un solo grupo.',
                      'fr': 'Répartissez des tâches entre deux équipes ou machines pour équilibrer leurs charges totales. Chaque '
                            'tâche appartient à un seul groupe.',
                      'de': 'Verteilen Sie Aufgaben auf zwei Teams oder Maschinen, sodass ihre Gesamtlast möglichst ähnlich ist. '
                            'Jede Aufgabe gehört genau einer Gruppe.'},
  'synthetic': {'kind': 'partition', 'variant': 'coupled', 'size': 2048, 'seed': 20261016}},
 {'id': 'projects',
  'title': {'en': 'Select projects', 'es': 'Selección de proyectos', 'fr': 'Choisir des projets', 'de': 'Projekte auswählen'},
  'description': {'en': 'Choose which projects to carry out, accounting for individual benefits, overlap costs and collaboration '
                        'gains.',
                  'es': 'Elige qué proyectos realizar, teniendo en cuenta sus beneficios, los costes por solapamiento y las '
                        'ventajas de colaborar.',
                  'fr': 'Choisissez les projets en tenant compte des bénéfices, coûts de chevauchement et gains de '
                        'collaboration.',
                  'de': 'Wähle Projekte unter Berücksichtigung von Nutzen, Überschneidungskosten und Kooperationsgewinnen.'},
  'help': {'en': 'benefits lists 2–128 positive benefit values. conflicts lists incompatible pairs using project numbers '
                 'starting at 1, for example [1,2]. Use [] if there are no conflicts. No duplicate pairs or self-conflicts. No '
                 'budget or deadline constraints in this model. For a generated large test, use Generate test data: size 4–4096 '
                 'and seed 0–2147483647. Keep the indicated variant; omit actual-data arrays. Generated tests use the large '
                 'model described in the examples, not the small template model.',
           'es': 'benefits contiene entre 2 y 128 beneficios positivos. conflicts contiene parejas incompatibles, usando números '
                 'de proyecto desde 1, por ejemplo [1,2]. Usa [] si no hay conflictos. No repitas parejas ni pongas un proyecto '
                 'contra sí mismo. Este modelo no admite presupuestos ni plazos. Para una prueba grande, pulsa Generar datos de '
                 'prueba: size 4–4096 y seed 0–2147483647. Mantén variant y no añadas tablas propias. La prueba generada usa el '
                 'modelo grande explicado en los ejemplos; la plantilla pequeña conserva el modelo descrito aquí.',
           'fr': 'benefits contient 2–128 bénéfices positifs. conflicts contient les paires incompatibles, numérotées à partir '
                 'de 1, par exemple [1,2]. Utilisez [] sans conflit. Aucune paire répétée ni conflit avec soi-même. Sans budget '
                 'ni échéances. Pour un grand test : Générer des données, size 4–4096 et seed 0–2147483647. Conservez variant, '
                 'sans tableaux de données propres. Le modèle généré est celui des exemples ; le petit modèle est décrit ici.',
           'de': 'benefits enthält 2–128 positive Nutzenwerte. conflicts enthält unvereinbare Paare mit Nummern ab 1, z. B. '
                 '[1,2]. Ohne Konflikte: []. Keine doppelten Paare oder Selbstkonflikte. Keine Budget- oder Terminregeln. Für '
                 'große Testdaten: Testdaten erzeugen, size 4–4096 und seed 0–2147483647. variant beibehalten, keine eigenen '
                 'Datentabellen ergänzen. Generierte Tests verwenden das Beispielmodell; die kleine Vorlage das hier '
                 'beschriebene Modell.'},
  'template': {'kind': 'projects', 'benefits': [12, 9, 7, 6], 'conflicts': [[1, 2], [2, 3]]},
  'own_description': {'en': 'Choose a set of compatible projects with the highest total benefit. Conflicting projects cannot '
                            'both be selected.',
                      'es': 'Elige proyectos compatibles para conseguir el mayor beneficio total. Dos proyectos marcados como '
                            'incompatibles no pueden elegirse juntos.',
                      'fr': 'Choisissez des projets compatibles pour maximiser le bénéfice total. Deux projets incompatibles ne '
                            'peuvent pas être sélectionnés ensemble.',
                      'de': 'Wählen Sie kompatible Projekte mit möglichst hohem Gesamtnutzen. Unvereinbare Projekte dürfen nicht '
                            'gemeinsam gewählt werden.'},
  'synthetic': {'kind': 'projects', 'variant': 'interactions', 'size': 2048, 'seed': 20261016}},
 {'id': 'assignment',
  'title': {'en': 'Assign jobs', 'es': 'Asignación de trabajos', 'fr': 'Affecter des travaux', 'de': 'Arbeiten zuordnen'},
  'description': {'en': 'Place each job in one of two compute pools, reducing execution costs, resource contention and '
                        'communication costs.',
                  'es': 'Coloca cada trabajo en uno de dos grupos de servidores, reduciendo costes de ejecución, recursos '
                        'compartidos y comunicación.',
                  'fr': 'Placez chaque travail dans un de deux groupes de serveurs pour réduire les coûts de calcul, de '
                        'ressources et de communication.',
                  'de': 'Ordne jede Arbeit einem von zwei Serverpools zu, um Ausführungs-, Ressourcen- und Kommunikationskosten '
                        'zu senken.'},
  'help': {'en': 'costs is a square table for 2–10 workers and the same number of jobs. Each row is a worker; each column is a '
                 'job. Use nonnegative numbers in the same unit. All assignments are allowed; no forbidden jobs or extra '
                 'constraints. For a generated large test, use Generate test data: size 4–4096 and seed 0–2147483647. Keep the '
                 'indicated variant; omit actual-data arrays. Generated tests use the large model described in the examples, not '
                 'the small template model.',
           'es': 'costs es una tabla cuadrada para 2–10 trabajadores y el mismo número de trabajos. Cada fila es un trabajador y '
                 'cada columna un trabajo. Usa costes no negativos en la misma unidad. Todas las asignaciones están permitidas; '
                 'no admite trabajos prohibidos ni reglas adicionales. Para una prueba grande, pulsa Generar datos de prueba: '
                 'size 4–4096 y seed 0–2147483647. Mantén variant y no añadas tablas propias. La prueba generada usa el modelo '
                 'grande explicado en los ejemplos; la plantilla pequeña conserva el modelo descrito aquí.',
           'fr': 'costs est un tableau carré pour 2–10 personnes et autant de travaux. Une ligne par personne, une colonne par '
                 'travail. Coûts positifs ou nuls dans la même unité. Toutes les affectations sont autorisées, sans règles '
                 'supplémentaires. Pour un grand test : Générer des données, size 4–4096 et seed 0–2147483647. Conservez '
                 'variant, sans tableaux de données propres. Le modèle généré est celui des exemples ; le petit modèle est '
                 'décrit ici.',
           'de': 'costs ist eine quadratische Tabelle für 2–10 Personen und ebenso viele Arbeiten. Zeilen sind Personen, Spalten '
                 'sind Arbeiten. Nichtnegative Kosten in derselben Einheit. Alle Zuordnungen sind erlaubt; keine zusätzlichen '
                 'Regeln. Für große Testdaten: Testdaten erzeugen, size 4–4096 und seed 0–2147483647. variant beibehalten, keine '
                 'eigenen Datentabellen ergänzen. Generierte Tests verwenden das Beispielmodell; die kleine Vorlage das hier '
                 'beschriebene Modell.'},
  'template': {'kind': 'assignment', 'costs': [[8, 2, 5], [4, 7, 3], [6, 4, 8]]},
  'own_description': {'en': 'Assign each job to one worker, and each worker to one job, minimizing the total cost. The table '
                            'says what each worker costs for each job.',
                      'es': 'Asigna un trabajo a cada trabajador y un trabajador a cada trabajo, minimizando el coste total. La '
                            'tabla indica cuánto cuesta cada combinación.',
                      'fr': 'Attribuez un travail à chaque personne et une personne à chaque travail, en minimisant le coût '
                            'total indiqué dans le tableau.',
                      'de': 'Ordnen Sie jeder Person genau eine Arbeit und jeder Arbeit genau eine Person zu. Minimiert werden '
                            'die Gesamtkosten aus der Tabelle.'},
  'synthetic': {'kind': 'assignment', 'variant': 'two_pools', 'size': 2048, 'seed': 20261016}},
 {'id': 'custom',
  'title': {'en': 'Advanced QUBO', 'es': 'QUBO avanzado', 'fr': 'QUBO avancé', 'de': 'QUBO erweitert'},
  'description': {'en': 'Optimize thousands of yes/no decisions with positive and negative costs between pairs. You can also '
                        'enter your own QUBO matrix.',
                  'es': 'Optimiza miles de decisiones sí/no con costes positivos y negativos entre parejas. También puedes '
                        'introducir tu propia matriz QUBO.',
                  'fr': 'Optimisez des milliers de décisions oui/non avec des coûts positifs et négatifs entre paires. Votre '
                        'propre matrice QUBO est aussi acceptée.',
                  'de': 'Optimiere Tausende Ja/Nein-Entscheidungen mit positiven und negativen Paarkosten. Eigene QUBO-Matrizen '
                        'sind ebenfalls möglich.'},
  'help': {'en': 'matrix is a square Q table with 2–128 rows. Both triangles are included in xᵀQx, so each off-diagonal pair is '
                 'added twice if Q is symmetric. Coefficients may be negative; absolute value at most 1000000. Optional offset: '
                 'absolute value at most 1000000000. Encode all constraints yourself; binary validity does not verify unstated '
                 'business rules. For a generated large test, use Generate test data: size 4–4096 and seed 0–2147483647. Keep '
                 'the indicated variant; omit actual-data arrays. Generated tests use the large model described in the examples, '
                 'not the small template model.',
           'es': 'matrix es la tabla cuadrada Q, de 2–128 filas. xᵀQx usa ambos triángulos: si Q es simétrica, cada pareja fuera '
                 'de la diagonal se suma dos veces. Se admiten coeficientes negativos, con valor absoluto máximo 1000000. offset '
                 'es opcional y su valor absoluto máximo es 1000000000. Debes incorporar las restricciones al modelo; comprobar '
                 'valores binarios no verifica reglas de negocio no expresadas. Para una prueba grande, pulsa Generar datos de '
                 'prueba: size 4–4096 y seed 0–2147483647. Mantén variant y no añadas tablas propias. La prueba generada usa el '
                 'modelo grande explicado en los ejemplos; la plantilla pequeña conserva el modelo descrito aquí.',
           'fr': 'matrix est un tableau Q carré de 2–128 lignes. xᵀQx utilise les deux triangles : chaque paire hors diagonale '
                 'est comptée deux fois si Q est symétrique. Coefficients signés, valeur absolue ≤1000000. offset facultatif, '
                 'valeur absolue ≤1000000000. Encodez vous-même toutes les contraintes métier. Pour un grand test : Générer des '
                 'données, size 4–4096 et seed 0–2147483647. Conservez variant, sans tableaux de données propres. Le modèle '
                 'généré est celui des exemples ; le petit modèle est décrit ici.',
           'de': 'matrix ist eine quadratische Q-Tabelle mit 2–128 Zeilen. xᵀQx nutzt beide Dreiecke; symmetrische Einträge '
                 'außerhalb der Diagonale werden zweimal addiert. Betrag der Koeffizienten ≤1000000; optionaler offset mit '
                 'Betrag ≤1000000000. Geschäftsregeln müssen im Modell codiert sein. Für große Testdaten: Testdaten erzeugen, '
                 'size 4–4096 und seed 0–2147483647. variant beibehalten, keine eigenen Datentabellen ergänzen. Generierte Tests '
                 'verwenden das Beispielmodell; die kleine Vorlage das hier beschriebene Modell.'},
  'template': {'kind': 'custom', 'matrix': [[-3, 2], [2, -2]], 'offset': 0},
  'own_description': {'en': 'Supply your own mathematical optimization model: choose binary values (0 or 1) that minimize xᵀQx + '
                            'offset.',
                      'es': 'Introduce tu propio modelo matemático: busca valores binarios (0 o 1) que minimicen xᵀQx + offset.',
                      'fr': 'Fournissez votre modèle mathématique : cherchez des valeurs binaires (0 ou 1) qui minimisent xᵀQx + '
                            'offset.',
                      'de': 'Geben Sie ein eigenes mathematisches Modell ein: Gesucht werden Binärwerte (0 oder 1), die xᵀQx + '
                            'offset minimieren.'},
  'synthetic': {'kind': 'custom', 'variant': 'dense', 'size': 2048, 'seed': 20261016}}]
PRESETS = [{'id': 'p1',
  'spec': {'kind': 'channels', 'size': 2048, 'seed': 20261017},
  'prompts': {'en': 'Problem 1 · Assign two channels to 2,048 transmitters to minimize same-channel interference. '
                    'Dense synthetic network, seed 20261017. Download the channel plan after running.',
              'es': 'Problem 1 · Asigna dos canales a 2048 transmisores para minimizar las interferencias entre los '
                    'que comparten canal. Red densa sintética, semilla 20261017. Descarga el plan de canales al '
                    'terminar.',
              'fr': 'Problem 1 · Attribuez deux canaux à 2048 émetteurs pour minimiser les interférences sur un même '
                    'canal. Réseau dense synthétique, graine 20261017. Téléchargez le plan après le calcul.',
              'de': 'Problem 1 · Weise 2048 Sendern zwei Kanäle zu, um Gleichkanalstörungen zu minimieren. Dichtes '
                    'synthetisches Netz, Seed 20261017. Lade anschließend den Kanalplan herunter.'},
  'category': 'channels',
  'explanation': {'en': 'Generated test with 2,048 transmitters and two channels. Case 20261017 reproduces the same '
                        'interference data.',
                  'es': 'Prueba generada con 2048 transmisores y dos canales. El caso 20261017 permite repetir los '
                        'mismos datos de interferencia.',
                  'fr': 'Test généré : 2048 émetteurs, deux canaux. Le cas 20261017 reproduit les mêmes données.',
                  'de': 'Generierter Test mit 2048 Sendern und zwei Kanälen. Fall 20261017 erzeugt dieselben '
                        'Stördaten.'}},
 {'id': 'p2',
  'spec': {'kind': 'channels', 'size': 1024, 'seed': 20261016},
  'prompts': {'en': 'Problem 2 · Assign two channels to 1,024 transmitters to minimize same-channel interference. '
                    'Dense synthetic network, seed 20261016. Download the channel plan after running.',
              'es': 'Problem 2 · Asigna dos canales a 1024 transmisores para minimizar las interferencias entre los '
                    'que comparten canal. Red densa sintética, semilla 20261016. Descarga el plan de canales al '
                    'terminar.',
              'fr': 'Problem 2 · Attribuez deux canaux à 1024 émetteurs pour minimiser les interférences sur un même '
                    'canal. Réseau dense synthétique, graine 20261016. Téléchargez le plan après le calcul.',
              'de': 'Problem 2 · Weise 1024 Sendern zwei Kanäle zu, um Gleichkanalstörungen zu minimieren. Dichtes '
                    'synthetisches Netz, Seed 20261016. Lade anschließend den Kanalplan herunter.'},
  'category': 'channels',
  'explanation': {'en': 'Generated test with 1,024 transmitters and two channels. Case 20261016 reproduces the same '
                        'interference data.',
                  'es': 'Prueba generada con 1024 transmisores y dos canales. El caso 20261016 permite repetir los '
                        'mismos datos de interferencia.',
                  'fr': 'Test généré : 1024 émetteurs, deux canaux. Le cas 20261016 reproduit les mêmes données.',
                  'de': 'Generierter Test mit 1024 Sendern und zwei Kanälen. Fall 20261016 erzeugt dieselben '
                        'Stördaten.'}},
 {'id': 'p3',
  'spec': {'kind': 'channels', 'size': 2048, 'seed': 20261016},
  'prompts': {'en': 'Problem 3 · Assign two channels to 2,048 transmitters to minimize same-channel interference. '
                    'Dense synthetic network, seed 20261016. Download the channel plan after running.',
              'es': 'Problem 3 · Asigna dos canales a 2048 transmisores para minimizar las interferencias entre los '
                    'que comparten canal. Red densa sintética, semilla 20261016. Descarga el plan de canales al '
                    'terminar.',
              'fr': 'Problem 3 · Attribuez deux canaux à 2048 émetteurs pour minimiser les interférences sur un même '
                    'canal. Réseau dense synthétique, graine 20261016. Téléchargez le plan après le calcul.',
              'de': 'Problem 3 · Weise 2048 Sendern zwei Kanäle zu, um Gleichkanalstörungen zu minimieren. Dichtes '
                    'synthetisches Netz, Seed 20261016. Lade anschließend den Kanalplan herunter.'},
  'category': 'channels',
  'explanation': {'en': 'Generated test with 2,048 transmitters and two channels. Case 20261016 reproduces the same '
                        'interference data.',
                  'es': 'Prueba generada con 2048 transmisores y dos canales. El caso 20261016 permite repetir los '
                        'mismos datos de interferencia.',
                  'fr': 'Test généré : 2048 émetteurs, deux canaux. Le cas 20261016 reproduit les mêmes données.',
                  'de': 'Generierter Test mit 2048 Sendern und zwei Kanälen. Fall 20261016 erzeugt dieselben '
                        'Stördaten.'}},
 {'id': 'p4',
  'spec': {'kind': 'channels', 'size': 512, 'seed': 20261016},
  'prompts': {'en': 'Problem 4 · Assign two channels to 512 transmitters to minimize same-channel interference. Dense '
                    'synthetic network, seed 20261016. Download the channel plan after running.',
              'es': 'Problem 4 · Asigna dos canales a 512 transmisores para minimizar las interferencias entre los que '
                    'comparten canal. Red densa sintética, semilla 20261016. Descarga el plan de canales al terminar.',
              'fr': 'Problem 4 · Attribuez deux canaux à 512 émetteurs pour minimiser les interférences sur un même '
                    'canal. Réseau dense synthétique, graine 20261016. Téléchargez le plan après le calcul.',
              'de': 'Problem 4 · Weise 512 Sendern zwei Kanäle zu, um Gleichkanalstörungen zu minimieren. Dichtes '
                    'synthetisches Netz, Seed 20261016. Lade anschließend den Kanalplan herunter.'},
  'category': 'channels',
  'explanation': {'en': 'Generated test with 512 transmitters and two channels. Case 20261016 reproduces the same '
                        'interference data.',
                  'es': 'Prueba generada con 512 transmisores y dos canales. El caso 20261016 permite repetir los '
                        'mismos datos de interferencia.',
                  'fr': 'Test généré : 512 émetteurs, deux canaux. Le cas 20261016 reproduit les mêmes données.',
                  'de': 'Generierter Test mit 512 Sendern und zwei Kanälen. Fall 20261016 erzeugt dieselben '
                        'Stördaten.'}},
 {'id': 'p5',
  'spec': {'kind': 'channels', 'size': 2048, 'seed': 20261018},
  'prompts': {'en': 'Problem 5 · Assign two channels to 2,048 transmitters to minimize same-channel interference. '
                    'Dense synthetic network, seed 20261018. Download the channel plan after running.',
              'es': 'Problem 5 · Asigna dos canales a 2048 transmisores para minimizar las interferencias entre los '
                    'que comparten canal. Red densa sintética, semilla 20261018. Descarga el plan de canales al '
                    'terminar.',
              'fr': 'Problem 5 · Attribuez deux canaux à 2048 émetteurs pour minimiser les interférences sur un même '
                    'canal. Réseau dense synthétique, graine 20261018. Téléchargez le plan après le calcul.',
              'de': 'Problem 5 · Weise 2048 Sendern zwei Kanäle zu, um Gleichkanalstörungen zu minimieren. Dichtes '
                    'synthetisches Netz, Seed 20261018. Lade anschließend den Kanalplan herunter.'},
  'category': 'channels',
  'explanation': {'en': 'Generated test with 2,048 transmitters and two channels. Case 20261018 reproduces the same '
                        'interference data.',
                  'es': 'Prueba generada con 2048 transmisores y dos canales. El caso 20261018 permite repetir los '
                        'mismos datos de interferencia.',
                  'fr': 'Test généré : 2048 émetteurs, deux canaux. Le cas 20261018 reproduit les mêmes données.',
                  'de': 'Generierter Test mit 2048 Sendern und zwei Kanälen. Fall 20261018 erzeugt dieselben '
                        'Stördaten.'}},
 {'id': 'p6',
  'spec': {'kind': 'channels', 'size': 2048, 'seed': 20261019},
  'prompts': {'en': 'Problem 6 · Assign two channels to 2,048 transmitters to minimize same-channel interference. '
                    'Dense synthetic network, seed 20261019. Download the channel plan after running.',
              'es': 'Problem 6 · Asigna dos canales a 2048 transmisores para minimizar las interferencias entre los '
                    'que comparten canal. Red densa sintética, semilla 20261019. Descarga el plan de canales al '
                    'terminar.',
              'fr': 'Problem 6 · Attribuez deux canaux à 2048 émetteurs pour minimiser les interférences sur un même '
                    'canal. Réseau dense synthétique, graine 20261019. Téléchargez le plan après le calcul.',
              'de': 'Problem 6 · Weise 2048 Sendern zwei Kanäle zu, um Gleichkanalstörungen zu minimieren. Dichtes '
                    'synthetisches Netz, Seed 20261019. Lade anschließend den Kanalplan herunter.'},
  'category': 'channels',
  'explanation': {'en': 'Generated test with 2,048 transmitters and two channels. Case 20261019 reproduces the same '
                        'interference data.',
                  'es': 'Prueba generada con 2048 transmisores y dos canales. El caso 20261019 permite repetir los '
                        'mismos datos de interferencia.',
                  'fr': 'Test généré : 2048 émetteurs, deux canaux. Le cas 20261019 reproduit les mêmes données.',
                  'de': 'Generierter Test mit 2048 Sendern und zwei Kanälen. Fall 20261019 erzeugt dieselben '
                        'Stördaten.'}},
 {'id': 'partition1',
  'category': 'partition',
  'spec': {'kind': 'partition', 'variant': 'coupled', 'size': 2048, 'seed': 20261016},
  'prompts': {'en': 'Problem 1 · 2,048 tasks. Split tasks between two teams, balancing workload and reducing '
                    'competition for shared resources. Synthetic data, seed 20261016.',
              'es': 'Problem 1 · 2,048 tareas. Reparte tareas entre dos equipos: equilibra la carga y reduce la '
                    'competencia por recursos compartidos. Datos sintéticos, semilla 20261016.',
              'fr': 'Problem 1 · 2,048 tâches. Répartissez les tâches entre deux équipes : équilibrez la charge et '
                    'réduisez la concurrence pour les ressources. Données synthétiques, graine 20261016.',
              'de': 'Problem 1 · 2,048 Aufgaben. Verteile Aufgaben auf zwei Teams: gleiche Lasten aus und verringere '
                    'Konflikte um gemeinsame Ressourcen. Synthetische Daten, Seed 20261016.'},
  'explanation': {'en': 'Two teams, with a cost for placing competing tasks together and for unequal workloads. All '
                        'tasks are assigned; balance is a cost, not an exact-equality constraint.',
                  'es': 'Dos equipos. Se penaliza juntar tareas que compiten por recursos y dejar cargas desiguales. '
                        'Todas las tareas se asignan; no se exige igualdad exacta.',
                  'fr': 'Deux équipes. Coût si des tâches concurrentes sont ensemble ou si les charges diffèrent. '
                        'Toutes les tâches sont affectées, sans égalité stricte.',
                  'de': 'Zwei Teams. Kosten für gemeinsam ausgeführte konkurrierende Aufgaben und ungleiche Lasten. '
                        'Jede Aufgabe wird zugeordnet; keine exakte Gleichheitsbedingung.'}},
 {'id': 'partition2',
  'category': 'partition',
  'spec': {'kind': 'partition', 'variant': 'coupled', 'size': 3072, 'seed': 20261017},
  'prompts': {'en': 'Problem 2 · 3,072 tasks. Split tasks between two teams, balancing workload and reducing '
                    'competition for shared resources. Synthetic data, seed 20261017.',
              'es': 'Problem 2 · 3,072 tareas. Reparte tareas entre dos equipos: equilibra la carga y reduce la '
                    'competencia por recursos compartidos. Datos sintéticos, semilla 20261017.',
              'fr': 'Problem 2 · 3,072 tâches. Répartissez les tâches entre deux équipes : équilibrez la charge et '
                    'réduisez la concurrence pour les ressources. Données synthétiques, graine 20261017.',
              'de': 'Problem 2 · 3,072 Aufgaben. Verteile Aufgaben auf zwei Teams: gleiche Lasten aus und verringere '
                    'Konflikte um gemeinsame Ressourcen. Synthetische Daten, Seed 20261017.'},
  'explanation': {'en': 'Two teams, with a cost for placing competing tasks together and for unequal workloads. All '
                        'tasks are assigned; balance is a cost, not an exact-equality constraint.',
                  'es': 'Dos equipos. Se penaliza juntar tareas que compiten por recursos y dejar cargas desiguales. '
                        'Todas las tareas se asignan; no se exige igualdad exacta.',
                  'fr': 'Deux équipes. Coût si des tâches concurrentes sont ensemble ou si les charges diffèrent. '
                        'Toutes les tâches sont affectées, sans égalité stricte.',
                  'de': 'Zwei Teams. Kosten für gemeinsam ausgeführte konkurrierende Aufgaben und ungleiche Lasten. '
                        'Jede Aufgabe wird zugeordnet; keine exakte Gleichheitsbedingung.'}},
 {'id': 'partition3',
  'category': 'partition',
  'spec': {'kind': 'partition', 'variant': 'coupled', 'size': 4096, 'seed': 20261018},
  'prompts': {'en': 'Problem 3 · 4,096 tasks. Split tasks between two teams, balancing workload and reducing '
                    'competition for shared resources. Synthetic data, seed 20261018.',
              'es': 'Problem 3 · 4,096 tareas. Reparte tareas entre dos equipos: equilibra la carga y reduce la '
                    'competencia por recursos compartidos. Datos sintéticos, semilla 20261018.',
              'fr': 'Problem 3 · 4,096 tâches. Répartissez les tâches entre deux équipes : équilibrez la charge et '
                    'réduisez la concurrence pour les ressources. Données synthétiques, graine 20261018.',
              'de': 'Problem 3 · 4,096 Aufgaben. Verteile Aufgaben auf zwei Teams: gleiche Lasten aus und verringere '
                    'Konflikte um gemeinsame Ressourcen. Synthetische Daten, Seed 20261018.'},
  'explanation': {'en': 'Two teams, with a cost for placing competing tasks together and for unequal workloads. All '
                        'tasks are assigned; balance is a cost, not an exact-equality constraint.',
                  'es': 'Dos equipos. Se penaliza juntar tareas que compiten por recursos y dejar cargas desiguales. '
                        'Todas las tareas se asignan; no se exige igualdad exacta.',
                  'fr': 'Deux équipes. Coût si des tâches concurrentes sont ensemble ou si les charges diffèrent. '
                        'Toutes les tâches sont affectées, sans égalité stricte.',
                  'de': 'Zwei Teams. Kosten für gemeinsam ausgeführte konkurrierende Aufgaben und ungleiche Lasten. '
                        'Jede Aufgabe wird zugeordnet; keine exakte Gleichheitsbedingung.'}},
 {'id': 'projects1',
  'category': 'projects',
  'spec': {'kind': 'projects', 'variant': 'interactions', 'size': 2048, 'seed': 20261016},
  'prompts': {'en': 'Problem 1 · 2,048 projects. Choose which projects to carry out, accounting for individual '
                    'benefits, overlap costs and collaboration gains. Synthetic data, seed 20261016.',
              'es': 'Problem 1 · 2,048 proyectos. Elige qué proyectos realizar, teniendo en cuenta sus beneficios, los '
                    'costes por solapamiento y las ventajas de colaborar. Datos sintéticos, semilla 20261016.',
              'fr': 'Problem 1 · 2,048 projets. Choisissez les projets en tenant compte des bénéfices, coûts de '
                    'chevauchement et gains de collaboration. Données synthétiques, graine 20261016.',
              'de': 'Problem 1 · 2,048 Projekte. Wähle Projekte unter Berücksichtigung von Nutzen, '
                    'Überschneidungskosten und Kooperationsgewinnen. Synthetische Daten, Seed 20261016.'},
  'explanation': {'en': 'Choose projects to maximize net value. Positive pair costs represent overlap; negative costs '
                        'represent collaboration. No budget limit or forbidden pairs.',
                  'es': 'Selecciona proyectos para maximizar el valor neto. Los costes positivos entre parejas son '
                        'solapamientos; los negativos, colaboración. Sin presupuesto límite ni parejas prohibidas.',
                  'fr': 'Maximisez la valeur nette. Les coûts positifs représentent les chevauchements, les négatifs '
                        'la collaboration. Sans budget limite ni paires interdites.',
                  'de': 'Maximiere den Nettonutzen. Positive Paarkosten stehen für Überschneidungen, negative für '
                        'Zusammenarbeit. Keine Budgetgrenze oder verbotenen Paare.'}},
 {'id': 'projects2',
  'category': 'projects',
  'spec': {'kind': 'projects', 'variant': 'interactions', 'size': 3072, 'seed': 20261017},
  'prompts': {'en': 'Problem 2 · 3,072 projects. Choose which projects to carry out, accounting for individual '
                    'benefits, overlap costs and collaboration gains. Synthetic data, seed 20261017.',
              'es': 'Problem 2 · 3,072 proyectos. Elige qué proyectos realizar, teniendo en cuenta sus beneficios, los '
                    'costes por solapamiento y las ventajas de colaborar. Datos sintéticos, semilla 20261017.',
              'fr': 'Problem 2 · 3,072 projets. Choisissez les projets en tenant compte des bénéfices, coûts de '
                    'chevauchement et gains de collaboration. Données synthétiques, graine 20261017.',
              'de': 'Problem 2 · 3,072 Projekte. Wähle Projekte unter Berücksichtigung von Nutzen, '
                    'Überschneidungskosten und Kooperationsgewinnen. Synthetische Daten, Seed 20261017.'},
  'explanation': {'en': 'Choose projects to maximize net value. Positive pair costs represent overlap; negative costs '
                        'represent collaboration. No budget limit or forbidden pairs.',
                  'es': 'Selecciona proyectos para maximizar el valor neto. Los costes positivos entre parejas son '
                        'solapamientos; los negativos, colaboración. Sin presupuesto límite ni parejas prohibidas.',
                  'fr': 'Maximisez la valeur nette. Les coûts positifs représentent les chevauchements, les négatifs '
                        'la collaboration. Sans budget limite ni paires interdites.',
                  'de': 'Maximiere den Nettonutzen. Positive Paarkosten stehen für Überschneidungen, negative für '
                        'Zusammenarbeit. Keine Budgetgrenze oder verbotenen Paare.'}},
 {'id': 'projects3',
  'category': 'projects',
  'spec': {'kind': 'projects', 'variant': 'interactions', 'size': 4096, 'seed': 20261018},
  'prompts': {'en': 'Problem 3 · 4,096 projects. Choose which projects to carry out, accounting for individual '
                    'benefits, overlap costs and collaboration gains. Synthetic data, seed 20261018.',
              'es': 'Problem 3 · 4,096 proyectos. Elige qué proyectos realizar, teniendo en cuenta sus beneficios, los '
                    'costes por solapamiento y las ventajas de colaborar. Datos sintéticos, semilla 20261018.',
              'fr': 'Problem 3 · 4,096 projets. Choisissez les projets en tenant compte des bénéfices, coûts de '
                    'chevauchement et gains de collaboration. Données synthétiques, graine 20261018.',
              'de': 'Problem 3 · 4,096 Projekte. Wähle Projekte unter Berücksichtigung von Nutzen, '
                    'Überschneidungskosten und Kooperationsgewinnen. Synthetische Daten, Seed 20261018.'},
  'explanation': {'en': 'Choose projects to maximize net value. Positive pair costs represent overlap; negative costs '
                        'represent collaboration. No budget limit or forbidden pairs.',
                  'es': 'Selecciona proyectos para maximizar el valor neto. Los costes positivos entre parejas son '
                        'solapamientos; los negativos, colaboración. Sin presupuesto límite ni parejas prohibidas.',
                  'fr': 'Maximisez la valeur nette. Les coûts positifs représentent les chevauchements, les négatifs '
                        'la collaboration. Sans budget limite ni paires interdites.',
                  'de': 'Maximiere den Nettonutzen. Positive Paarkosten stehen für Überschneidungen, negative für '
                        'Zusammenarbeit. Keine Budgetgrenze oder verbotenen Paare.'}},
 {'id': 'assignment1',
  'category': 'assignment',
  'spec': {'kind': 'assignment', 'variant': 'two_pools', 'size': 2048, 'seed': 20261016},
  'prompts': {'en': 'Problem 1 · 2,048 jobs. Place each job in one of two compute pools, reducing execution costs, '
                    'resource contention and communication costs. Synthetic data, seed 20261016.',
              'es': 'Problem 1 · 2,048 trabajos. Coloca cada trabajo en uno de dos grupos de servidores, reduciendo '
                    'costes de ejecución, recursos compartidos y comunicación. Datos sintéticos, semilla 20261016.',
              'fr': 'Problem 1 · 2,048 travaux. Placez chaque travail dans un de deux groupes de serveurs pour réduire '
                    'les coûts de calcul, de ressources et de communication. Données synthétiques, graine 20261016.',
              'de': 'Problem 1 · 2,048 Arbeiten. Ordne jede Arbeit einem von zwei Serverpools zu, um Ausführungs-, '
                    'Ressourcen- und Kommunikationskosten zu senken. Synthetische Daten, Seed 20261016.'},
  'explanation': {'en': 'Each job goes to pool A or B. Some pairs compete in the same pool; others communicate and '
                        'cost more when separated. No capacity limit.',
                  'es': 'Cada trabajo va al grupo A o B. Algunas parejas compiten en el mismo grupo; otras se '
                        'comunican y cuestan más si se separan. Sin límite de capacidad.',
                  'fr': 'Chaque travail va au groupe A ou B. Certaines paires se concurrencent ensemble ; d’autres '
                        'coûtent plus lorsqu’elles sont séparées. Sans limite de capacité.',
                  'de': 'Jede Arbeit geht an Pool A oder B. Manche Paare konkurrieren im selben Pool, andere '
                        'verursachen bei Trennung Kommunikationskosten. Keine Kapazitätsgrenze.'}},
 {'id': 'assignment2',
  'category': 'assignment',
  'spec': {'kind': 'assignment', 'variant': 'two_pools', 'size': 3072, 'seed': 20261017},
  'prompts': {'en': 'Problem 2 · 3,072 jobs. Place each job in one of two compute pools, reducing execution costs, '
                    'resource contention and communication costs. Synthetic data, seed 20261017.',
              'es': 'Problem 2 · 3,072 trabajos. Coloca cada trabajo en uno de dos grupos de servidores, reduciendo '
                    'costes de ejecución, recursos compartidos y comunicación. Datos sintéticos, semilla 20261017.',
              'fr': 'Problem 2 · 3,072 travaux. Placez chaque travail dans un de deux groupes de serveurs pour réduire '
                    'les coûts de calcul, de ressources et de communication. Données synthétiques, graine 20261017.',
              'de': 'Problem 2 · 3,072 Arbeiten. Ordne jede Arbeit einem von zwei Serverpools zu, um Ausführungs-, '
                    'Ressourcen- und Kommunikationskosten zu senken. Synthetische Daten, Seed 20261017.'},
  'explanation': {'en': 'Each job goes to pool A or B. Some pairs compete in the same pool; others communicate and '
                        'cost more when separated. No capacity limit.',
                  'es': 'Cada trabajo va al grupo A o B. Algunas parejas compiten en el mismo grupo; otras se '
                        'comunican y cuestan más si se separan. Sin límite de capacidad.',
                  'fr': 'Chaque travail va au groupe A ou B. Certaines paires se concurrencent ensemble ; d’autres '
                        'coûtent plus lorsqu’elles sont séparées. Sans limite de capacité.',
                  'de': 'Jede Arbeit geht an Pool A oder B. Manche Paare konkurrieren im selben Pool, andere '
                        'verursachen bei Trennung Kommunikationskosten. Keine Kapazitätsgrenze.'}},
 {'id': 'assignment3',
  'category': 'assignment',
  'spec': {'kind': 'assignment', 'variant': 'two_pools', 'size': 4096, 'seed': 20261018},
  'prompts': {'en': 'Problem 3 · 4,096 jobs. Place each job in one of two compute pools, reducing execution costs, '
                    'resource contention and communication costs. Synthetic data, seed 20261018.',
              'es': 'Problem 3 · 4,096 trabajos. Coloca cada trabajo en uno de dos grupos de servidores, reduciendo '
                    'costes de ejecución, recursos compartidos y comunicación. Datos sintéticos, semilla 20261018.',
              'fr': 'Problem 3 · 4,096 travaux. Placez chaque travail dans un de deux groupes de serveurs pour réduire '
                    'les coûts de calcul, de ressources et de communication. Données synthétiques, graine 20261018.',
              'de': 'Problem 3 · 4,096 Arbeiten. Ordne jede Arbeit einem von zwei Serverpools zu, um Ausführungs-, '
                    'Ressourcen- und Kommunikationskosten zu senken. Synthetische Daten, Seed 20261018.'},
  'explanation': {'en': 'Each job goes to pool A or B. Some pairs compete in the same pool; others communicate and '
                        'cost more when separated. No capacity limit.',
                  'es': 'Cada trabajo va al grupo A o B. Algunas parejas compiten en el mismo grupo; otras se '
                        'comunican y cuestan más si se separan. Sin límite de capacidad.',
                  'fr': 'Chaque travail va au groupe A ou B. Certaines paires se concurrencent ensemble ; d’autres '
                        'coûtent plus lorsqu’elles sont séparées. Sans limite de capacité.',
                  'de': 'Jede Arbeit geht an Pool A oder B. Manche Paare konkurrieren im selben Pool, andere '
                        'verursachen bei Trennung Kommunikationskosten. Keine Kapazitätsgrenze.'}},
 {'id': 'custom1',
  'category': 'custom',
  'spec': {'kind': 'custom', 'variant': 'dense', 'size': 2048, 'seed': 20261016},
  'prompts': {'en': 'Problem 1 · 2,048 binary decisions. Optimize thousands of yes/no decisions with positive and '
                    'negative costs between pairs. You can also enter your own QUBO matrix. Synthetic data, seed '
                    '20261016.',
              'es': 'Problem 1 · 2,048 decisiones binarias. Optimiza miles de decisiones sí/no con costes positivos y '
                    'negativos entre parejas. También puedes introducir tu propia matriz QUBO. Datos sintéticos, '
                    'semilla 20261016.',
              'fr': 'Problem 1 · 2,048 décisions binaires. Optimisez des milliers de décisions oui/non avec des coûts '
                    'positifs et négatifs entre paires. Votre propre matrice QUBO est aussi acceptée. Données '
                    'synthétiques, graine 20261016.',
              'de': 'Problem 1 · 2,048 Binärentscheidungen. Optimiere Tausende Ja/Nein-Entscheidungen mit positiven '
                    'und negativen Paarkosten. Eigene QUBO-Matrizen sind ebenfalls möglich. Synthetische Daten, Seed '
                    '20261016.'},
  'explanation': {'en': 'A dense signed interaction model with local preferences. The answer is a vector of zeros and '
                        'ones; a lower objective is better.',
                  'es': 'Modelo denso con interacciones positivas y negativas y preferencias individuales. La '
                        'respuesta es una lista de ceros y unos; cuanto menor el objetivo, mejor.',
                  'fr': 'Modèle dense à interactions signées et préférences individuelles. Réponse binaire ; un '
                        'objectif plus faible est meilleur.',
                  'de': 'Dichtes Modell mit positiven und negativen Wechselwirkungen sowie lokalen Präferenzen. Binäre '
                        'Antwort; ein kleinerer Zielfunktionswert ist besser.'}},
 {'id': 'custom2',
  'category': 'custom',
  'spec': {'kind': 'custom', 'variant': 'dense', 'size': 3072, 'seed': 20261017},
  'prompts': {'en': 'Problem 2 · 3,072 binary decisions. Optimize thousands of yes/no decisions with positive and '
                    'negative costs between pairs. You can also enter your own QUBO matrix. Synthetic data, seed '
                    '20261017.',
              'es': 'Problem 2 · 3,072 decisiones binarias. Optimiza miles de decisiones sí/no con costes positivos y '
                    'negativos entre parejas. También puedes introducir tu propia matriz QUBO. Datos sintéticos, '
                    'semilla 20261017.',
              'fr': 'Problem 2 · 3,072 décisions binaires. Optimisez des milliers de décisions oui/non avec des coûts '
                    'positifs et négatifs entre paires. Votre propre matrice QUBO est aussi acceptée. Données '
                    'synthétiques, graine 20261017.',
              'de': 'Problem 2 · 3,072 Binärentscheidungen. Optimiere Tausende Ja/Nein-Entscheidungen mit positiven '
                    'und negativen Paarkosten. Eigene QUBO-Matrizen sind ebenfalls möglich. Synthetische Daten, Seed '
                    '20261017.'},
  'explanation': {'en': 'A dense signed interaction model with local preferences. The answer is a vector of zeros and '
                        'ones; a lower objective is better.',
                  'es': 'Modelo denso con interacciones positivas y negativas y preferencias individuales. La '
                        'respuesta es una lista de ceros y unos; cuanto menor el objetivo, mejor.',
                  'fr': 'Modèle dense à interactions signées et préférences individuelles. Réponse binaire ; un '
                        'objectif plus faible est meilleur.',
                  'de': 'Dichtes Modell mit positiven und negativen Wechselwirkungen sowie lokalen Präferenzen. Binäre '
                        'Antwort; ein kleinerer Zielfunktionswert ist besser.'}},
 {'id': 'custom3',
  'category': 'custom',
  'spec': {'kind': 'custom', 'variant': 'dense', 'size': 4096, 'seed': 20261018},
  'prompts': {'en': 'Problem 3 · 4,096 binary decisions. Optimize thousands of yes/no decisions with positive and '
                    'negative costs between pairs. You can also enter your own QUBO matrix. Synthetic data, seed '
                    '20261018.',
              'es': 'Problem 3 · 4,096 decisiones binarias. Optimiza miles de decisiones sí/no con costes positivos y '
                    'negativos entre parejas. También puedes introducir tu propia matriz QUBO. Datos sintéticos, '
                    'semilla 20261018.',
              'fr': 'Problem 3 · 4,096 décisions binaires. Optimisez des milliers de décisions oui/non avec des coûts '
                    'positifs et négatifs entre paires. Votre propre matrice QUBO est aussi acceptée. Données '
                    'synthétiques, graine 20261018.',
              'de': 'Problem 3 · 4,096 Binärentscheidungen. Optimiere Tausende Ja/Nein-Entscheidungen mit positiven '
                    'und negativen Paarkosten. Eigene QUBO-Matrizen sind ebenfalls möglich. Synthetische Daten, Seed '
                    '20261018.'},
  'explanation': {'en': 'A dense signed interaction model with local preferences. The answer is a vector of zeros and '
                        'ones; a lower objective is better.',
                  'es': 'Modelo denso con interacciones positivas y negativas y preferencias individuales. La '
                        'respuesta es una lista de ceros y unos; cuanto menor el objetivo, mejor.',
                  'fr': 'Modèle dense à interactions signées et préférences individuelles. Réponse binaire ; un '
                        'objectif plus faible est meilleur.',
                  'de': 'Dichtes Modell mit positiven und negativen Wechselwirkungen sowie lokalen Präferenzen. Binäre '
                        'Antwort; ein kleinerer Zielfunktionswert ist besser.'}}]
