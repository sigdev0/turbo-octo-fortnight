"""
OmniForge V2 Cultural Documentary Video Library — "Mesin Waktu Nusantara".
Implements historical documentary archetypes benchmarked to Medan Amrulloh (@medanamrulloh).
Calibrated 4-movement narrations (240-340 words, ~60-90s spoken at 130-140 WPM)
paired with 4 cinematic Ken Burns scenes and Midjourney/Flux visual prompts.
"""

from typing import Dict, Any, List
import re

ARCHETYPES_METADATA: Dict[str, Dict[str, Any]] = {
    "majapahit_trowulan": {
        "title_id": "Ibukota Bata Merah & Kejayaan Wilwatikta (1350 M)",
        "title_en": "Red Brick Capital & The Glory of Wilwatikta (1350 CE)",
        "era": "1350 Masehi (Era Hayam Wuruk & Gajah Mada)",
        "narration": (
            "Bayangkan kamu berdiri di gerbang Trowulan pada puncak kejayaan abad ke-14. Udara lembap tropis "
            "Jawa Timur berhembus perlahan, membawa semerbak aroma dupa kemenyan, bunga cempaka kuning, dan tanah liat "
            "basah yang dibakar sempurna. Di hadapan matamu menjulang megah Gapura Bajang Ratu, mahakarya bata merah "
            "terakota setinggi belasan meter yang dipahat rumit tanpa perekat semen, bersinar hangat diterpa cahaya "
            "matahari senja keemasan. Langkah kakimu disambut denting genta perunggu para pendeta Siwa-Buddha serta tatapan "
            "waspada prajurit Bhayangkara berpakaian sutra jingga dengan keris berluk tersemat gagah di pinggang mereka. "
            "Melangkah lebih dalam ke jantung kota metropolitan Wilwatikta, kamu menyaksikan kanal-kanal air teratur "
            "membelah pemukiman batu bata, tempat perahu-perahu kayu berlalu lalang mengangkut rempah dan kain tenun. "
            "Di tepi Kolam Segaran seluas enam setengah hektar, perjamuan agung para bangsawan tengah berlangsung meriah. "
            "Denting cawan emas dan tempayan porselen halus berpadu dengan alunan lembut gamelan pelog. Di pasar kota, "
            "saudagar dari Campa, India, Persia, dan Tiongkok Dinasti Yuan bertransaksi menggunakan keping uang kepeng "
            "perunggu dengan penuh keakraban. Para pandai besi dan pengrajin terakota sibuk mengukir arca dan menempa "
            "senjata pusaka terbaik. Lalu, di Balai Manguntur Tangkil, suasana mendadak hening ketika Mahapatih Gajah Mada "
            "melangkah ke hadapan takhta Prabu Hayam Wuruk. Dengan suara menggelegar dan tatapan membakar, ia mengumandangkan "
            "Sumpah Palapa: pantang mengecap kenikmatan duniawi sebelum seluruh kepulauan Nusantara bersatu di bawah panji surya "
            "Wilwatikta. Sumpah keramat itu dibuktikan dengan meluncurnya ratusan jung kayu raksasa berlayar menguasai samudra "
            "raya, menjaga kedaulatan maritim dari Selat Malaka hingga kepulauan Maluku. Trowulan bukan sekadar reruntuhan "
            "bata merah masa lalu, melainkan monumen abadi jiwa bangsa kita. Dari sanalah lahir semboyan suci Bhinneka "
            "Tunggal Ika Tan Hana Dharma Mangrwa, bukti luhur bahwa keberagaman suku, keyakinan, dan lautan adalah kekayaan "
            "sejati yang memersatukan peradaban Nusantara sepanjang zaman."
        ),
        "narration_en": (
            "Imagine standing before the monumental gateway of Trowulan at the zenith of the fourteenth century. "
            "The warm tropical breeze carries the sweet fragrance of burning sandalwood, yellow champaca flowers, and "
            "kiln-fired clay. Towering directly before you rises Bajang Ratu, an architectural wonder of interlocking "
            "red terracotta bricks sculpted without a drop of mortar, glowing radiant in the amber rays of equatorial "
            "dusk. Your arrival is greeted by the resonance of bronze temple bells and the vigilant gaze of elite "
            "Bhayangkara guards adorned in fine silk sashes, sacred wavy-bladed keris daggers tucked proudly at their sides. "
            "Venturing deeper into the metropolitan heart of Wilwatikta, engineered water canals divide bustling brick wards "
            "where wooden transport barges ferry harvest, aromatic spices, and woven textiles. Beside the vast waters of the "
            "Segaran reservoir, noble banquets unfold under carved timber pavilions. Golden goblets clink against celadon "
            "porcelain to the meditative chimes of pelog bronze gamelan. In the central bazaar, merchants from Champa, "
            "southern India, Arabia, and the Yuan Dynasty trade with brass coins amidst animated chatter, while master "
            "smiths forge legendary ceremonial blades and sculpt terracotta reliefs. Suddenly, an expectant silence "
            "envelops the royal courtyard as Prime Minister Gajah Mada steps before the throne of King Hayam Wuruk. With an "
            "echoing voice and unyielding resolve, he pronounces the sacred Palapa Oath: refusing worldly respite until every "
            "island and sea of Nusantara unites under Wilwatikta's sovereign banner. That oath unleashed armada junks across "
            "treacherous oceans, establishing complete mastery from the Malacca Strait to the spice islands of Maluku. "
            "Trowulan was never just an ancient capital of terracotta brick, but the living soul of our archipelago. Here "
            "was born the eternal truth of Unity in Diversity, proving that harmony across diverse cultures and seas is "
            "Nusantara's timeless gift to humanity."
        ),
        "scenes": [
            {
                "visual_prompt": (
                    "cinematic 8k photography, ancient Majapahit gateway Bajang Ratu, monumental red terracotta "
                    "brick archway, golden hour volumetric lighting, intricate relief carvings, mist rolling "
                    "over stone paved courtyard, historical reconstruction, photorealistic, 35mm lens, f/1.8"
                ),
                "camera_motion": "zoom_in_center",
                "caption_title": "Gerbang Bajang Ratu",
                "caption_body": "Gapura terakota bata merah abad ke-14 berdiri kokoh tanpa semen perekat."
            },
            {
                "visual_prompt": (
                    "ultra-detailed wide shot of Segaran Reservoir Trowulan 1350 AD, tranquil reflective water, "
                    "ancient brick embankments, royal wooden pavilion with golden lanterns, merchants from Champa "
                    "and China trading silks and porcelain, cinematic atmospheric haze, photorealistic documentary"
                ),
                "camera_motion": "pan_horizontal_reveal",
                "caption_title": "Kolam Segaran",
                "caption_body": "Waduk buatan seluas 6,5 hektar pusat perjamuan megah kerajaan Majapahit."
            },
            {
                "visual_prompt": (
                    "dramatic historical portrait, Mahapatih Gajah Mada swearing Sumpah Palapa in front of "
                    "King Hayam Wuruk, Manguntur Tangkil pavilion, bronze oil lamps, royal banners of Wilwatikta, "
                    "intense determined expression, intricate Javanese batik sarong, golden keris, chiaroscuro lighting"
                ),
                "camera_motion": "zoom_out_monumental",
                "caption_title": "Sumpah Palapa",
                "caption_body": "Gajah Mada bersumpah menyatukan seluruh samudra dan kepulauan Nusantara."
            },
            {
                "visual_prompt": (
                    "epic sunset panorama, massive Majapahit wooden naval junks sailing through Java Sea, "
                    "red and white pennants flying, glowing terracotta coastal citadels in background, golden reflections "
                    "on ocean waves, 8k cinematic masterpiece, National Geographic documentary style"
                ),
                "camera_motion": "dramatic_tilt_up",
                "caption_title": "Kejayaan Bahari Wilwatikta",
                "caption_body": "Armada maritim terkuat mengawal kedaulatan jalur rempah dunia."
            }
        ]
    },

    "sriwijaya_maritim": {
        "title_id": "Penguasa Musipura & Poros Maritim Dunia (abad ke-8)",
        "title_en": "Rulers of Musipura & Global Maritime Nexus (8th Century)",
        "era": "Abad ke-8 Masehi (Kedatuan Sriwijaya)",
        "narration": (
            "Melangkah seribu dua ratus tahun ke masa lalu, kamu tiba di muara Sungai Musi yang terbentang megah. "
            "Kabut fajar perlahan tersibak oleh hembusan angin laut, memperlihatkan ratusan kapal cadik Samudraraksa dan "
            "jung samudra berlabuh rapat di pelabuhan Musipura. Udara pagi pekat oleh semerbak wangi kayu gaharu pilihan, "
            "kapur barus baros, dan tumpukan karung rempah pala cengkih yang siap berlayar menuju pelabuhan India, Persia, "
            "dan Tiongkok Dinasti Tang. Air pasang berkilau memantulkan dermaga kayu ulin hitam tempat ribuan kelasi dari "
            "berbagai benua bersandar dengan takjub. Di atas tanggul kota suci, biksu-biksu terpelajar berjubah safron "
            "berjalan beriringan dengan langkah tenang, melantunkan bait-bait suci dalam bahasa Sanskerta. Kedatuan Sriwijaya "
            "adalah mercusuar ilmu pengetahuan dan pusat universitas Buddhis terbesar di seantero Asia Tenggara. Di tempat "
            "inilah sarjana termasyhur asal Tiongkok, I-Tsing, menghabiskan waktu bertahun-tahun untuk menerjemahkan kitab "
            "suci sebelum melanjutkan ziarah ke Nalanda. Denting merdu genta biara berpadu dengan nyanyian burung rawa dan "
            "riak air Sungai Musi yang tenang mengalir. Namun di balik keheningan spiritual itu, tersimpan kekuatan maritim "
            "yang sangat disegani di seluruh penjuru bumi. Di bawah komando sang Datu, para ksatria Orang Laut yang tangguh "
            "mengawal Selat Malaka dengan disiplin baja. Mereka menumpas perompak tanpa ampun dan menjamin keamanan mutlak "
            "bagi seluruh kapal niaga dunia. Prasasti suci Talang Tuwo mencatat titah luhur Sri Jayanasa: membangun taman "
            "hutan Sriksetra untuk kemakmuran semua makhluk hidup tanpa membedakan kasta maupun derajat. Dari riak air Musipura, "
            "Sriwijaya mewariskan kebijaksanaan agung bahari kita: bahwa kekuasaan sejati tidak dibangun dengan penindasan di "
            "daratan, melainkan dengan merajut tali persaudaraan samudra, keterbukaan ilmu pengetahuan, dan diplomasi perdamaian "
            "yang dihormati peradaban dunia."
        ),
        "narration_en": (
            "Stepping twelve centuries into the past, you arrive at the sweeping estuary of the Musi River. The dawn "
            "mist slowly parts before the maritime breeze, revealing hundreds of double-outrigger Samudraraksa galleons and "
            "towering sea junks anchored in the harbor of Musipura. The morning air hangs heavy with the intoxicating scent of "
            "wild agarwood, pure Barus camphor, and dried clove bundles destined for imperial ports in India, Persia, and Tang "
            "Dynasty China. The shimmering high tide laps against ancient ironwood jetties where cosmopolitan sailors dock in "
            "shared wonder. Along the embankments of this sacred capital, scholarly monks clad in saffron robes stroll serenely, "
            "reciting verses in classical Sanskrit. The Kedatuan of Sriwijaya was the intellectual beacon and paramount Buddhist "
            "university of Southeast Asia. Here, celebrated Chinese pilgrim-scholar I-Tsing spent formative years translating "
            "profound manuscripts before continuing his journey to Nalanda. Bronze monastery bells chime over the tranquil waters, "
            "accompanied by forest songbirds and the gentle rhythm of the river currents. Yet behind this contemplative tranquility "
            "lay a naval force respected across continents. Guided by the sovereign Datu, the intrepid Orang Laut seafaring warriors "
            "commanded the Malacca Strait with unyielding discipline. They eradicated piracy and established the safest international "
            "maritime trade passage on earth. Upon sacred stone tablets, the Talang Tuwo inscription records the king's compassionate "
            "decree: constructing lush botanical sanctuaries for the welfare, sustenance, and delight of all living beings without "
            "distinction. From the tides of Musipura, Sriwijaya bequeathed an enduring maritime truth: that genuine greatness is "
            "not conquered by brute territorial force, but forged through sea connections, universal knowledge, and principled "
            "diplomacy respected across civilizations."
        ),
        "scenes": [
            {
                "visual_prompt": (
                    "cinematic 8k photograph, ancient 8th century Sriwijaya harbor on Musi River, dozens of traditional "
                    "Samudraraksa outrigger ships with woven sails, sunrise mist, ironwood jetties, barrels of spices "
                    "and agarwood, National Geographic documentary photography, hyper-detailed, golden lighting"
                ),
                "camera_motion": "zoom_in_center",
                "caption_title": "Pelabuhan Musipura",
                "caption_body": "Muara Sungai Musi menjadi simpul maritim teramai antara India dan Dinasti Tang."
            },
            {
                "visual_prompt": (
                    "scholarly Buddhist monastery in ancient Palembang 750 AD, red timber pavilions with curved eaves, "
                    "monks in saffron robes examining palm-leaf Sanskrit manuscripts, Chinese scholar monk I-Tsing, "
                    "bronze stupika bells, serene reflection pond with blooming lotuses, soft morning light"
                ),
                "camera_motion": "pan_horizontal_reveal",
                "caption_title": "Pusat Studi Sanskerta",
                "caption_body": "Pusat universitas Buddhis dunia tempat sarjana lintas benua menimba ilmu."
            },
            {
                "visual_prompt": (
                    "epic naval shot of Orang Laut warriors on armed war prahus patrolling Malacca Strait, "
                    "carved dragon prow, brass cannons, shields, emerald ocean waters, stormy dramatic clouds, "
                    "cinematic dynamic composition, historical documentary realism"
                ),
                "camera_motion": "zoom_out_monumental",
                "caption_title": "Penjaga Selat Malaka",
                "caption_body": "Armada laut tangguh menjamin keamanan jalur perdagangan dunia bebas perompak."
            },
            {
                "visual_prompt": (
                    "solemn royal ceremony, Datu of Sriwijaya consecrating the Talang Tuwo inscription stone, "
                    "luxurious golden jewelry, sacred water vessels, lush green forest park sanctuary background, "
                    "volumetric sunlight rays piercing through ancient canopy, cinematic 8k"
                ),
                "camera_motion": "dramatic_tilt_up",
                "caption_title": "Prasasti Talang Tuwo",
                "caption_body": "Kearifan ekologis abad ke-8: titah raja membangun taman hutan untuk kesejahteraan rakyat."
            }
        ]
    },

    "padjajaran_siliwangi": {
        "title_id": "Kerajaan Pakuan di Balik Kabut Gunung Salak (abad ke-15)",
        "title_en": "Pakuan Kingdom Behind Mount Salak Mist (15th Century)",
        "era": "Abad ke-15 Masehi (Era Prabu Siliwangi)",
        "narration": (
            "Di bawah naungan rimbun Gunung Salak yang berselimut kabut putih tebal, kamu melangkah melintasi gerbang utama "
            "Pakuan Pajajaran pada abad ke-15. Suara deru air terjun dan gemercik aliran Sungai Ciliwung serta Cisadane "
            "terdengar deras mengelilingi parit pertahanan tanah yang kokoh menjulang. Udara dingin pegunungan Parahyangan "
            "terasa begitu menyegarkan dada, dipenuhi wangi harum daun hanjuang merah, getah pinus basah, dan aroma tanah "
            "gembur sehabis hujan lebat. Setiap sudut kota memancarkan ketenangan yang bersahabat dan penuh wibawa. "
            "Di sepanjang jalan berbatu kali yang bersih, masyarakat Sunda menyambut pagi dengan senyum tulus dan tutur kata "
            "yang santun. Mereka memikul lumbung bambu berisi padi huma, menganyam keranjang rotan dengan motif pusaka, dan "
            "merawat kebun sirih pinang di lereng-lereng perbukitan hijau. Rumah-rumah panggung kayu jati beratap ijuk hitam "
            "berdiri selaras dengan lekuk bukit tanpa merusak sebatang pohon pun di hutan tutupan. Prajurit Pajajaran berpakaian "
            "serba putih berdiri tegak menggenggam kujang pusaka bercabang tiga, menjadi benteng moral bagi kebenaran dan kehormatan "
            "tanah pusaka. Di Keraton Sri Bima Punta Narayana, Sri Baduga Maharaja Prabu Siliwangi memimpin musyawarah bersama para "
            "sesepuh dengan kehangatan seorang ayah agung. Ajaran luhur Silih Asih, Silih Asah, dan Silih Asuh bukan hanya semboyan "
            "di atas kertas kropak, melainkan nafas hidup yang ditaati seluruh rakyat. Di tanah ini, kejayaan kerajaan tidak pernah "
            "dihitung dari tumpukan peti emas, melainkan dari lumbung leuit rakyat yang selalu penuh dan tidur malam warga yang "
            "tenteram tanpa rasa takut. Pakuan Pajajaran adalah pelukan abadi kearifan ekologis Nusantara. Dari hutan larangan "
            "Priangan, para leluhur berpesan kepada kita: jagalah bumi pertiwi selaras dengan nurani, rawatlah sesama manusia "
            "dengan welas asih, niscaya kedamaian sejati akan memayungi negeri hingga akhir masa."
        ),
        "narration_en": (
            "Beneath the forested slopes of Mount Salak shrouded in dense silver mist, you pass through the southern "
            "ramparts of Pakuan Pajajaran in the fifteenth century. The rushing waters of the Ciliwung and Cisadane rivers "
            "thunder below, forming an impenetrable natural moat around formidable earthen embankments. The cool mountain air "
            "of Parahyangan fills your lungs with revitalizing sweetness, carrying notes of sacred red hanjuang leaves, "
            "rain-soaked pine sap, and rich volcanic loam. Every avenue radiates serene dignity and tranquil warmth. Along "
            "stone-paved highland lanes, Sundanese villagers greet the dawn with gentle smiles and melodic greetings. Farmers "
            "carry harvest baskets overflowing with upland rice, craftspeople weave intricate bamboo patterns, and elders tend "
            "sacred hillside gardens. Traditional timber stilt residences crowned with black palm thatch rise in flawless "
            "equilibrium with the hill contours, strictly preserving the sacred taboo forests. Guardian sentinels in pure "
            "white garments hold three-pronged curved kujang daggers, vigilant protectors of spiritual integrity and royal honor. "
            "Within the open timber palace of Sri Bima, King Siliwangi presides over communal gatherings with the benevolence of a "
            "loving patriarch. The sacred creed of loving, teaching, and nurturing one another flourished as the living heartbeat "
            "of daily life. In this highland sanctuary, royal prosperity was measured not by hoarded treasures of gold, but by "
            "overflowing community granaries and citizens sleeping peacefully through the night without fear. Pakuan Pajajaran "
            "stands as an eternal monument to Nusantara's ecological wisdom. From the mist-veiled forests of ancient Sunda, "
            "our ancestors teach that when humanity respects the living earth and honors human dignity, peace and abundance "
            "endure forever."
        ),
        "scenes": [
            {
                "visual_prompt": (
                    "cinematic 8k photography, Pakuan Pajajaran royal gate made of polished dark teakwood and ijuk thatch, "
                    "Mount Salak looming in background shrouded in misty clouds, rushing river moat below, lush tropical "
                    "ferns, guards in white traditional attire holding sacred kujang, volumetric cinematic lighting"
                ),
                "camera_motion": "zoom_in_center",
                "caption_title": "Gerbang Pakuan Pajajaran",
                "caption_body": "Benteng alam diapit Sungai Ciliwung dan Cisadane di bawah bayang-bayang Gunung Salak."
            },
            {
                "visual_prompt": (
                    "traditional 15th century Sundanese village settlement, stilt wooden houses with steep roofs, "
                    "golden rice terraces on rolling hills, morning mist, villagers in simple woven garments, "
                    "smoke rising from clay hearths, peaceful pastoral documentary atmosphere, National Geographic style"
                ),
                "camera_motion": "pan_horizontal_reveal",
                "caption_title": "Harmoni Parahyangan",
                "caption_body": "Kehidupan masyarakat yang hidup selaras dengan alam dan hutan larangan."
            },
            {
                "visual_prompt": (
                    "historical portrait of Sri Baduga Maharaja Prabu Siliwangi seated in royal wooden pavilion, "
                    "dignified benevolent smile, traditional white Sundanese turban and batik cloth, sacred tiger emblem, "
                    "warm golden oil lantern light, ancient stone inscriptions nearby, cinematic depth of field"
                ),
                "camera_motion": "zoom_out_monumental",
                "caption_title": "Prabu Siliwangi",
                "caption_body": "Pemimpin bijaksana pembawa era keemasan Sunda dengan ajaran Silih Asih, Asah, dan Asuh."
            },
            {
                "visual_prompt": (
                    "macro cinematic shot of sacred bronze and iron Kujang blade resting on stone plinth, "
                    "delicate engravings, mountain river valley in soft focus background, dawn sunrise rays illuminating "
                    "the blade steel, 8k documentary quality, mystical atmospheric realism"
                ),
                "camera_motion": "dramatic_tilt_up",
                "caption_title": "Kujang Pusaka Sunda",
                "caption_body": "Simbol kemandirian, ketajaman budi pekerti, dan pelindung tanah pusaka."
            }
        ]
    },

    "borobudur_syailendra": {
        "title_id": "Gunung Kebajikan di Atas Lembah Menoreh (abad ke-9)",
        "title_en": "Mountain of Virtue Above Menoreh Valley (9th Century)",
        "era": "Abad ke-9 Masehi (Wangsa Syailendra)",
        "narration": (
            "Fajar abad ke-9 baru saja menyingsing di atas Lembah Kedu yang subur menghijau. Kabut perak perlahan terangkat dari "
            "sela bukit Menoreh, menyingkap kemegahan mahakarya yang menembus batas nalar arsitektur manusia: Candi Borobudur yang "
            "baru selesai dipahat sempurna. Lebih dari dua juta balok batu andesit vulkanik tersusun rapat dengan kuncian takik "
            "presisi tanpa setitik pun semen perekat, membentuk mandala kosmis raksasa yang merekah laksana bunga teratai suci di "
            "atas perbukitan purba. Udara pagi yang hening dan sejuk dipenuhi gema ritmis palu perunggu para pemahat batu yang "
            "tengah memoles relief terakhir. Ribuan meter bidang batu andesit bercerita tentang perjalanan jiwa manusia. Relief "
            "Karmawibhangga di kaki candi memaparkan hukum sebab akibat dengan kejujuran tanpa batas, sementara relief Lalitavistara "
            "mengabadikan kisah agung sang Buddha menuju pencerahan sejati. Peziarah berjubah putih dari Sri Lanka, India, dan "
            "kepulauan Nusantara mendaki undakan teras berundak Kamadhatu menuju Rupadhatu dengan langkah khidmat dan kepala tertunduk "
            "penuh rasa hormat. Bau harum minyak dupa cendana membubung tinggi ke angkasa biru muda. Di teras lingkaran tertinggi "
            "Arupadhatu, dunia kasat mata seolah memudar lenyap. Tujuh puluh dua stupa batu berongga berdiri melingkar mengelilingi "
            "stupa induk raksasa yang menatap sunyi ke arah puncak Gunung Merapi yang mengepulkan asap tipis. Di balik teralis batu "
            "berlubang belah ketupat, arca-arca Buddha tersenyum tenang dalam samadi abadi. Dibangun oleh Wangsa Syailendra selama "
            "puluhan tahun gotong royong tanpa paksaan, candi ini adalah bukti tingginya peradaban spiritual nenek moyang kita. "
            "Borobudur bukan sekadar tumpukan andesit mati, melainkan doa agung yang dipahatkan di bumi Nusantara. Candi ini mengingatkan "
            "kita bahwa puncak peradaban tertinggi tidak diukur dari bala tentara penakluk, melainkan dari keluhuran moral, cinta "
            "kasih universal, dan kemurnian jiwa yang mencerahkan dunia."
        ),
        "narration_en": (
            "The dawn of the ninth century breaks softly over the lush, emerald expanses of the Kedu Valley. Silver "
            "morning mists lift from the ridges of the Menoreh hills to unveil an architectural wonder beyond human "
            "imagination: the freshly completed mandala of Borobudur. Over two million volcanic andesite blocks interlock with "
            "flawless mortise-and-tenon joints, rising like a monumental sacred stone lotus blossomed atop an ancient sanctuary "
            "hill. The crisp morning air resonates with the gentle clinking of bronze chisels as master sculptors polish the final "
            "decorative panels. Kilometers of dark stone surfaces chronicle the spiritual pilgrimage of existence. At the base, the "
            "Karmawibhangga reliefs depict the immutable law of cause and effect, while higher tiers illustrate the profound path "
            "to enlightenment. Devout pilgrims in unblemished white garments from Sri Lanka, India, and across island kingdoms ascend "
            "the concentric stone terraces of desire and form in silent awe. The fragrance of burning sandalwood incense drifts "
            "upward into the pristine morning sky. Reaching the circular terraces of the formless sphere, material boundaries "
            "dissolve into quiet infinity. Seventy-two perforated andesite stupas encircle the grand central dome, gazing peacefully "
            "across the valley toward the smoking silhouette of Mount Merapi. Inside the diamond-latticed stone enclosures, serene "
            "Buddhas rest in eternal contemplation. Erected across generations of cooperative devotion by the Sailendra dynasty, "
            "this monument represents the apex of ancient spiritual engineering. Borobudur is never merely a monument of volcanic "
            "rock, but an immortal prayer chiseled upon the earth. It stands as an enduring testament that true civilizational "
            "triumph lies not in military conquest, but in boundless compassion, ethical integrity, and the elevation of the "
            "human soul."
        ),
        "scenes": [
            {
                "visual_prompt": (
                    "cinematic 8k sunrise shot of Borobudur temple in 850 AD, newly constructed pristine dark andesite stone, "
                    "mist floating across Kedu Valley, Mount Merapi emitting gentle smoke plume in distant horizon, "
                    "golden morning rays striking stupas, National Geographic masterpiece, wide angle"
                ),
                "camera_motion": "zoom_in_center",
                "caption_title": "Fajar Lembah Kedu",
                "caption_body": "Dua juta balok batu andesit vulkanik disusun membentuk mandala suci kosmos."
            },
            {
                "visual_prompt": (
                    "intricate close-up of ancient Javanese stone carvers working on Karmawibhangga relief panel, "
                    "bronze hammer and chisel, stone dust particles caught in morning sunbeam, hyper-detailed facial expressions "
                    "of sculptors, authentic 9th century artisan clothing, photorealistic documentary"
                ),
                "camera_motion": "pan_horizontal_reveal",
                "caption_title": "Pahatan Karmawibhangga",
                "caption_body": "Ribuan relief dinding mengajarkan hukum moral sebab-akibat dan welas asih."
            },
            {
                "visual_prompt": (
                    "silent reverent pilgrims ascending the stone stairways of Borobudur, oil lamps glowing at dawn, "
                    "incense smoke curling into the cool air, towering stone guardian dwarapala statues, "
                    "epic atmospheric depth, historical realism"
                ),
                "camera_motion": "zoom_out_monumental",
                "caption_title": "Pendakian Spiritual",
                "caption_body": "Peziarah mancanegara menapaki tangga dari alam nafsu menuju kesucian batin."
            },
            {
                "visual_prompt": (
                    "monumental view of Borobudur circular summit terrace, perforated andesite stupas, seated stone Buddha "
                    "partially visible through diamond latticework, majestic Menoreh mountain panorama at sunset, "
                    "cinematic volumetric dusk lighting, 8k resolution"
                ),
                "camera_motion": "dramatic_tilt_up",
                "caption_title": "Puncak Arupadhatu",
                "caption_body": "Stupa induk melambangkan kebebasan jiwa dan kedamaian sejati peradaban."
            }
        ]
    },

    "singasari_kenarok": {
        "title_id": "Darah, Keris, dan Titik Mula Takdir Jawa (1222 M)",
        "title_en": "Blood, Keris, and the Origin of Javanese Destiny (1222 CE)",
        "era": "1222 Masehi (Berdirinya Kerajaan Tumapel / Singasari)",
        "narration": (
            "Tahun seribu dua ratus dua puluh dua Masehi, bumi Tumapel bergetar hebat oleh derap ribuan langkah prajurit perang. "
            "Di lereng Gunung Kawi yang kelabu berbalut kabut belerang, denting palu pandai besi Mpu Gandring membakar keheningan "
            "malam dengan percikan api pijar berwarna merah saga. Di atas paron batu hitam, sebilah keris bertuah baru saja rampung "
            "ditempa, membawa takdir darah dan kutukan tujuh keturunan raja-raja tanah Jawa. Udara malam terasa dingin menusuk "
            "tulang, namun sorot mata Ken Arok menyala bagai lahar membara menatap masa depan yang belum tertulis. Ken Arok bangkit "
            "dari kepapaan rakyat jelata, meruntuhkan kekuasaan Tunggul Ametung, dan mempersunting Ken Dedes, putri jelita yang "
            "dipuja sebagai Sri Nareswari, ibu agung penitis para penguasa Nusantara. Di padang rumput Ganter, pasukan Tumapel "
            "berhadapan langsung dengan armada perang Kerajaan Kediri dalam pertempuran hidup dan mati yang menentukan arah sejarah. "
            "Sorak perang menggelegar menembus cakrawala saat bendera Panji merah-putih berkibar gagah membelah kabut fajar. "
            "Kemenangan mutlak di Ganter meruntuhkan tatanan lama dan melahirkan Wangsa Rajasa yang perkasa. Dari reruntuhan itu, "
            "berdirilah Kerajaan Singasari yang menorehkan babak baru keberanian Jawa. Di bawah panji Singasari kelak, Prabu "
            "Kertanegara melancarkan Ekspedisi Pamalayu untuk merajut persaudaraan antarpulau serta dengan gagah berani mengusir "
            "utusan perang Kaisar Kubilai Khan dari Mongol. Kemegahan Candi Singosari yang kokoh dijaga arca raksasa Dwarapala "
            "menjadi bukti keteguhan jiwa yang tak pernah sudi tunduk pada bangsa asing mana pun di muka bumi. Singasari adalah "
            "kawah candradimuka watak ksatria Nusantara. Dari kobaran api Tumapel inilah lahir keberanian untuk menolak takdir "
            "kekalahan, membakar semangat kemandirian bangsa, dan menabur benih kejayaan yang kelak menjelma menjadi imperium "
            "agung Majapahit di persada Nusantara."
        ),
        "narration_en": (
            "In the fateful year of twelve twenty-two, the volcanic earth of Tumapel shook violently beneath the disciplined "
            "march of thousands of warriors. On the slopes of Mount Kawi shrouded in sulfurous ash, the hammer of master "
            "swordsmith Mpu Gandring shattered the midnight silence with cascading showers of crimson sparks. Upon a dark basalt "
            "anvil, a legendary keris was tempered in fire, bearing the fateful curse destined to claim seven generations of "
            "Javanese kings. The nocturnal mountain air bit cold, yet Ken Arok's eyes burned with the fury of molten lava. "
            "Rising from common obscurity through sheer will, Ken Arok seized power from governor Tunggul Ametung and wed Ken Dedes, "
            "the radiant queen revered as Sri Nareswari, divine mother of all future rulers of Java. Across the open plains of "
            "Ganter, Singasari clashed with the royal forces of Kediri in an epic showdown that permanently transformed regional "
            "history. Thundering battle shouts rent the horizon as Tumapel's red-and-white banners unfurled through the morning "
            "mist. This decisive victory dismantled the ancient order and birthed the formidable Rajasa dynasty. Upon this foundation "
            "arose the Kingdom of Singasari, inaugurating a daring chapter of maritime and regional independence. It was Singasari "
            "that launched the Pamalayu expedition to unite neighboring islands and brazenly defied the imperial demands of Mongol "
            "Emperor Kublai Khan. The imposing stone sanctuary of Candi Singosari, guarded by colossal Dwarapala statues wielding stone "
            "maces, stands as an unshakeable monument to sovereignty that refused to kneel before any foreign empire. Singasari was the "
            "crucible that forged the warrior spirit of Nusantara. From the flames of Tumapel sprang the audacity to shatter "
            "limitations, ignite self-determination, and plant the fertile seeds that would blossom into the glorious golden age of "
            "Majapahit."
        ),
        "scenes": [
            {
                "visual_prompt": (
                    "cinematic 8k photography, ancient Javanese forge at night, blacksmith Mpu Gandring hammering glowing "
                    "red hot Damascus steel keris on stone anvil, embers flying, dramatic chiaroscuro fiery lighting, "
                    "smoke and shadows in mountain workshop, historical realism"
                ),
                "camera_motion": "zoom_in_center",
                "caption_title": "Tempaan Keris Gandring",
                "caption_body": "Keris pusaka ditempa dengan kutukan takdir tujuh keturunan raja-raja Jawa."
            },
            {
                "visual_prompt": (
                    "regal historical portrait of Ken Dedes standing in royal stone pavilion, radiant glowing aura, "
                    "exquisite antique batik cloth, golden crown, Ken Arok watching from the shadows, "
                    "dramatic candlelit courtyard, Mount Kawi silhouette, cinematic 35mm lens"
                ),
                "camera_motion": "pan_horizontal_reveal",
                "caption_title": "Sri Nareswari Ken Dedes",
                "caption_body": "Ibu agung yang melahirkan garis keturunan raja-raja besar tanah Jawa."
            },
            {
                "visual_prompt": (
                    "epic historical battle of Ganter 1222 AD, Singasari warriors led by Ken Arok charging into battle, "
                    "bronze shields, raised spears, billowing red and white banners, dust storm over green battlefield, "
                    "dramatic morning sky, National Geographic war documentary style"
                ),
                "camera_motion": "zoom_out_monumental",
                "caption_title": "Pertempuran Padang Ganter",
                "caption_body": "Kemenangan mutlak Ken Arok meruntuhkan dominasi Kediri dan melahirkan Dinasti Rajasa."
            },
            {
                "visual_prompt": (
                    "majestic grey andesite Candi Singosari temple monument at twilight, towering monolithic structure, "
                    "fierce guardian dwarapala giants in foreground holding stone maces, ominous storm clouds, "
                    "atmospheric cinematic lighting, 8k resolution"
                ),
                "camera_motion": "dramatic_tilt_up",
                "caption_title": "Warisan Candi Singosari",
                "caption_body": "Cikal bakal imperium maritim yang kelak menantang serbuan pasukan Mongol."
            }
        ]
    }
}

ARCHETYPE_ALIASES: Dict[str, str] = {
    # Majapahit
    "majapahit": "majapahit_trowulan",
    "trowulan": "majapahit_trowulan",
    "gajah mada": "majapahit_trowulan",
    "gajahmada": "majapahit_trowulan",
    "hayam wuruk": "majapahit_trowulan",
    "wilwatikta": "majapahit_trowulan",
    "bajang ratu": "majapahit_trowulan",
    "palapa": "majapahit_trowulan",
    # Sriwijaya
    "sriwijaya": "sriwijaya_maritim",
    "musipura": "sriwijaya_maritim",
    "palembang": "sriwijaya_maritim",
    "sungai musi": "sriwijaya_maritim",
    "musi": "sriwijaya_maritim",
    "maritim": "sriwijaya_maritim",
    "bahari": "sriwijaya_maritim",
    "i-tsing": "sriwijaya_maritim",
    "itsing": "sriwijaya_maritim",
    # Pajajaran / Sunda
    "pajajaran": "padjajaran_siliwangi",
    "padjajaran": "padjajaran_siliwangi",
    "siliwangi": "padjajaran_siliwangi",
    "pakuan": "padjajaran_siliwangi",
    "sunda": "padjajaran_siliwangi",
    "salak": "padjajaran_siliwangi",
    "kujang": "padjajaran_siliwangi",
    "parahyangan": "padjajaran_siliwangi",
    # Borobudur
    "borobudur": "borobudur_syailendra",
    "syailendra": "borobudur_syailendra",
    "sailendra": "borobudur_syailendra",
    "candi": "borobudur_syailendra",
    "menoreh": "borobudur_syailendra",
    "kedu": "borobudur_syailendra",
    "stupa": "borobudur_syailendra",
    "buddha": "borobudur_syailendra",
    # Singasari
    "singasari": "singasari_kenarok",
    "singosari": "singasari_kenarok",
    "ken arok": "singasari_kenarok",
    "kenarok": "singasari_kenarok",
    "tumapel": "singasari_kenarok",
    "ken dedes": "singasari_kenarok",
    "kendedes": "singasari_kenarok",
    "mpu gandring": "singasari_kenarok",
    "gandring": "singasari_kenarok",
    "keris": "singasari_kenarok",
    "ganter": "singasari_kenarok",
}


def select_cultural_archetype(query: str) -> str:
    """
    Normalizes user input or search keywords to one of the 5 canonical historical archetypes.
    Defaults to 'majapahit_trowulan' if no exact match is found.
    """
    q = (query or "").lower().strip()
    if not q:
        return "majapahit_trowulan"

    # Direct match on archetype key
    if q in ARCHETYPES_METADATA:
        return q

    # Check aliases
    for alias, archetype in ARCHETYPE_ALIASES.items():
        if alias in q:
            return archetype

    # Fallback deterministic rotation by hash
    keys = list(ARCHETYPES_METADATA.keys())
    return keys[abs(hash(q)) % len(keys)]


def get_documentary_story(archetype: str, is_id: bool = True) -> Dict[str, Any]:
    """
    Fetches the calibrated script, scene prompts, camera motions, and metadata
    for a chosen historical archetype.
    """
    arch_key = archetype if archetype in ARCHETYPES_METADATA else select_cultural_archetype(archetype)
    data = ARCHETYPES_METADATA[arch_key]

    narration_text = data["narration"] if is_id else data.get("narration_en", data["narration"])
    title_text = data["title_id"] if is_id else data.get("title_en", data["title_id"])

    return {
        "archetype": arch_key,
        "title": title_text,
        "title_id": data["title_id"],
        "title_en": data.get("title_en", data["title_id"]),
        "era": data["era"],
        "narration": narration_text,
        "scenes": data["scenes"],
        "word_count": len(narration_text.split())
    }
