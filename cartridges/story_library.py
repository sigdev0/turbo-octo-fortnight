"""
OmniForge V2 Deep Sleep Story Library.
Provides calibrated, multi-movement bedtime stories (380-450 words for toddlers, 650-750 words for older kids)
incorporating authentic Indonesian storytelling archetypes and Global English translations.
"""

from typing import Dict, Tuple, Any

# ==============================================================================
# 1. BAHASA INDONESIA: TODDLER (Age <= 3) Target: 380 - 450 words
# ==============================================================================

def _toddler_pinisi_id(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"Malam telah tiba di pesisir pantai yang tenang dan damai... "
        f"Semilir angin laut berhembus lembut, membelai pipi halus si kecil {name}. "
        f"Tarik napas perlahan... rasakan udara malam yang sejuk dan bersih masuk ke dada... "
        f"lalu hembuskan dengan nyaman, perlahan, dan sangat lega... "
        f"Tubuh mungilmu kini terasa begitu hangat, rileks, dan aman di atas peraduan yang empuk. "
        f"Di tepian pantai berpasir putih selembut tepung, bersandar sebuah perahu pinisi kecil berukir bunga melati yang indah. "
        f"Perahu pinisi ini bertabur bantal-bantal sutra tebal dan selimut tenun hangat bermotif awan perak. "
        f"Bulan purnama tersenyum ramah dari langit malam yang biru pekat, memantulkan cahaya keperakan di atas riak air laut yang tenang. "
        f"Si kecil {name} melangkah perlahan masuk ke dalam perahu pinisi bersama boneka kesayangan... lalu berbaring dengan begitu nyaman di bawah naungan atap bambu. "
        f"Perahu pinisi mulai berayun perlahan... berayun ke kiri... lalu berayun ke kanan... "
        f"Mengikuti alunan irama ombak kecil yang berbisik lembut membelai pantai pasir putih. "
        f"Di sekeliling perahu, air laut berkilauan bagai taburan mutiara kecil yang berkelip hangat... "
        f"Itulah cahaya kedamaian dari teluk {theme} yang indah, tenang, dan menyejukkan. "
        f"Seekor kura-kura laut kecil dengan cangkang berkilau hijau zamrud berenang mendekat di sisi lambung perahu. "
        f"Kura-kura laut itu menatap si kecil {name} dengan penuh kehangatan, lalu berbisik lembut, "
        f"'Selamat malam, sahabat cilik {name}... Samudra luas yang tenteram ini selalu menjagamu dalam kehangatan dan {lesson}.' "
        f"Bintang-bintang di angkasa tinggi mengedipkan sinarnya yang ramah, menyelimuti malammu dengan rasa aman yang mendalam. "
        f"Ikan-ikan kecil di terumbu karang yang warna-warni telah melipat sirip mereka, beristirahat nyaman di balik ayunan rumput laut yang sejuk. "
        f"Bintang laut di dasar pasir berkedip redup, mengucapkan salam tidur yang penuh kasih sayang. "
        f"Burung camar malam pun telah hinggap damai di atas dahan bakau yang kokoh, menutup matanya dengan tenang. "
        f"Kini suasana di sekelilingmu menjadi semakin hening... Shhh... Tenang sekali... Sungguh damai... "
        f"Kelopak matamu mulai terasa semakin berat... begitu berat dan mengantuk... "
        f"Napasmu menjadi semakin pelan, teratur, dan begitu ringan... seperti alunan air laut yang tenang. "
        f"Setiap hembusan napas melepaskan semua rasa lelah dari seharian bermain riang. "
        f"Punggungmu hangat... tangan dan kakimu terasa sangat santai dan lemas tanpa beban. "
        f"Kamu adalah anak yang sangat baik, anak yang manis, dan senantiasa disayangi oleh seluruh keluargamu. "
        f"Pejamkan matamu perlahan, penjelajah cilik... Biarkan perahu pinisi membawamu meluncur anggun menuju pulau mimpi yang paling indah. "
        f"Tidurlah yang nyenyak di pelukan malam yang hangat dan aman ini... "
        f"Selamat tidur, sayangku {name}... Selamat malam... Mimpi indah..."
    )

def _toddler_kalpataru_id(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"Malam telah turun dengan anggun di atas rindangnya hutan tropis Nusantara yang tenang... "
        f"Di kamar tidurmu yang hangat ini, si kecil {name} bersiap untuk menyambut mimpi indah. "
        f"Tarik napas dalam-dalam perlahan... rasakan ketenangan malam mengisi hatimu... "
        f"lalu hembuskan pelan-pelan... melepaskan segala ketegangan dengan rasa nyaman yang luar biasa... "
        f"Rasakan betapa empuk dan nyamannya kasur dan bantal tidurmu malam ini... Kamu sangat aman, kamu sangat tenang. "
        f"Jauh di dalam pelukan alam yang sunyi, berdiri sebatang Pohon Kalpataru yang agung dan penuh keajaiban. "
        f"Daun-daun pohon itu memancarkan pendar cahaya hijau zamrud yang hangat, lembut, dan menyejukkan pandangan mata. "
        f"Di bawah naungan dahan-dahan pohon yang damai ini, sahabat-sahabat kecil hutan sedang bersiap untuk tidur lelap. "
        f"Si kecil {name} berbaring di atas hamparan permadani lumut hutan yang luar biasa tebal, bersih, dan harum. "
        f"Kancil kecil yang bijak merebahkan kepalanya dengan santai di samping kakimu, meringkuk nyaman. "
        f"Burung Cendrawasih yang rupawan melipat sayap emasnya yang kemilau di atas dahan pohon, bersiul pelan sebuah lagu tidur yang syahdu. "
        f"Kancil kecil menatap {name} dengan tatapan mata yang hangat dan penuh kasih sayang, lalu berbisik lembut, "
        f"'Tidurlah dengan nyenyak, wahai {name}... Hari ini kamu telah membawa begitu banyak senyuman dan {lesson} bagi dunia.' "
        f"Angin malam berhembus lembut melewati celah dedaunan, membawa aroma wangi bunga kenanga dan melati hutan yang harum semerbak. "
        f"Bunga-bunga anggrek hutan menutup kelopaknya perlahan, menyimpan embun malam yang sejuk di tangkainya yang lentur. "
        f"Tetesan embun malam menetes perlahan dari pucuk daun... Tik... tok... begitu ritmis, tenang, dan menenangkan jiwa. "
        f"Seluruh penghuni hutan kini telah memejamkan mata mereka dalam keheningan yang syahdu dan damai. "
        f"Rusa-rusa kecil tertidur pulas di balik rumpun bambu yang bergoyang pelan ditiup angin sepoi-sepoi. "
        f"Tupai-tupai pohon kecil telah meringkuk di dalam lubang kayu yang hangat, saling mendekap erat dalam kenyamanan. "
        f"Kupu-kupu malam hinggap tenang di atas kelopak bunga, menutup sayap cantiknya tanpa bersuara. "
        f"Tubuh mungilmu terasa semakin hangat, semakin rileks, dan tenggelam nyaman ke dalam dekapan kasurmu yang empuk. "
        f"Dengarkan desir daun yang meninabobokanmu... Shhh... Istirahatlah sekarang... Semuanya aman dan damai... "
        f"Kelopak matamu semakin berat... tak perlu lagi terbuka... Rasakan kehangatan selimutmu membungkus seluruh tubuhmu. "
        f"Napasmu mengalir pelan, teratur, dan lembut bagai hembusan angin sepoi-sepoi. "
        f"Otot-otot di pundakmu dan tangan mungilmu kini benar-benar rileks dan santai tanpa beban. "
        f"Kamu adalah permata hati yang berharga dan selalu dilindungi dengan limpahan cinta yang tak pernah habis. "
        f"Pejamkan matamu, sahabat cilik... Biarkan keajaiban hutan membawamu ke negeri tidur yang paling lelap. "
        f"Selamat tidur, sayangku {name}... Selamat malam... Istirahatlah dengan damai..."
    )

def _toddler_awan_id(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"Malam telah tiba menyelimuti lereng-lereng perbukitan dengan selimut kabut putih yang lembut... "
        f"Si kecil {name} bersandar nyaman di peraduan, memandang ke arah langit malam yang bertabur bintang kejora. "
        f"Tarik napas perlahan dan dalam... rasakan udara sejuk beraroma melati mengisi seluruh dadamu... "
        f"lalu hembuskan perlahan-lahan... membiarkan seluruh tubuhmu menjadi ringan dan santai... "
        f"Di atas puncak bukit yang sunyi, aroma daun teh yang segar berpadu dengan wanginya bunga sedap malam. "
        f"Dari angkasa yang tinggi, sebuah awan putih yang sangat lembut melayang turun perlahan menyapa jendela kamarmu. "
        f"Awan itu sehangat kepompong sutra, seputih kapas murni, dan selembut pelukan kasih seorang ibu tercinta. "
        f"Awan putih itu mengajak si kecil {name} untuk berbaring santai di atas punggungnya yang empuk dan harum. "
        f"Rasakan betapa nyaman dan hangatnya kelembutan awan itu merangkul seluruh punggung, tangan, dan kakimu. "
        f"Awan berarak pelan di langit malam negeri {theme}... Melintasi perbukitan hijau yang kini mulai terlelap tidur. "
        f"Di kejauhan, kelinci-kelinci awan kecil meringkuk damai di samping bulan sabit yang keemasan. "
        f"Bulan tersenyum lembut memandang {name}, lalu membisikkan doa tidur yang menenangkan jiwa, "
        f"'Selamat malam anak yang baik, {name}... Langit malam ini melindungimu dengan penuh kasih sayang dan {lesson}.' "
        f"Bintang-bintang kecil membentuk tirai pendar keemasan, menghangatkan setiap sudut ruang tidurmu dengan cahaya tenang. "
        f"Bunga-bunga awan mekar tanpa suara, menebarkan wangi vanila dan chamomile yang menyejukkan hati. "
        f"Kini kabut malam turun semakin tebal, membungkus sekelilingmu dalam keheningan yang menyejukkan dan damai. "
        f"Tak ada suara yang tergesa-gesa... Semua bintang meredupkan pendar cahayanya agar kamu bisa tidur nyenyak. "
        f"Burung camar langit melipat sayapnya di puncak awan, tertidur pulas dalam pelukan malam yang syahdu. "
        f"Angin pegunungan berbisik lembut mengelus keningmu, mengusap lembut setiap helai rambutmu. "
        f"Burung kepodang emas hinggap di ranting awan, memejamkan matanya dengan tenteram dan tenang. "
        f"Lonceng angin perak berdentang sangat halus di kejauhan... ting... ting... mengantar tidur yang lelap. "
        f"Shhh... Tenang sekali... Sungguh nyaman, tenteram, dan damai... "
        f"Kelopak matamu terasa semakin berat dan mengantuk... sangat berat untuk dibuka kembali... "
        f"Detak jantung dan napasmu melambat dengan ritme yang teratur, tenang, dan begitu damai. "
        f"Seluruh jemari tangan dan kakimu terasa hangat, rileks, dan lemas bersandar pada kasurmu yang empuk. "
        f"Hari ini telah selesai dengan sangat indah, dan esok matahari akan menyapamu dengan keceriaan baru. "
        f"Kamu adalah anak yang sangat disayangi, berharga, dan dilindungi selamanya. "
        f"Biarkan tubuhmu terlelap sepenuhnya di atas awan mimpi yang empuk... "
        f"Selamat tidur nyenyak, sayangku {name}... Selamat malam... Tidurlah dalam damai..."
    )

def _toddler_kunang_id(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"Matahari telah terbenam di balik ufuk barat, meninggalkan lembah hijau yang tenang dalam kehangatan senja... "
        f"Si kecil {name} kini berbaring santai di tempat tidurnya yang empuk, bersiap untuk mengistirahatkan tubuh mungilnya. "
        f"Tarik napas pelan-pelan... rasakan udara malam yang sejuk mengalir tenang ke dalam dadamu... "
        f"lalu hembuskan napasmu dengan sangat lembut... melepaskan segala rasa lelah bermain seharian ini... "
        f"Selimut tidurmu terasa begitu hangat membungkus ujung jari-jari kakimu hingga ke pundakmu yang santai. "
        f"Di tepi sungai kecil yang airnya mengalir jernih tanpa riak, ribuan lentera kunang-kunang mulai menyalakan cahaya emasnya. "
        f"Cahaya kunang-kunang itu berkelip lembut dan teratur... menyala perlahan... lalu meredup pelan... bagai detak napas malam yang syahdu. "
        f"Seekor kunang-kunang kecil yang ramah hinggap perlahan di atas dahan bambu dekat peraduan si kecil {name}. "
        f"Kunang-kunang itu membawa sebuah lentera cahaya mungil yang beraroma wangi daun pandan dan madu hutan yang menenangkan. "
        f"Kunang-kunang bersuara lembut bagai nyanyian dawai kecapi yang mengalun lirih di kejauhan, "
        f"'Selamat malam, anak manis {name}... Lembah sungai yang tenang ini menemani tidurmu dalam kehangatan {lesson}.' "
        f"Air sungai mengalir pelan... gemericik airnya terdengar begitu ritmis... mengalir pelan... terus mengalir menenangkan... "
        f"Bunga-bunga teratai di atas permukaan telaga telah mengatupkan kelopak daunnya untuk tidur pulas di bawah sinar rembulan. "
        f"Ikan-ikan mas kecil menyelam ke dasar kolam berpasir halus, memejamkan mata dalam ketenangan air yang sejuk. "
        f"Katak-katak pohon kecil bernyanyi dengan nada bisikan yang semakin lama semakin pelan... hingga akhirnya tertidur pulas. "
        f"Bebek-bebek air menyembunyikan paruh mereka di balik bulu-bulu hangat di tepian rawa yang tenang. "
        f"Semak-semak belukar di tepi sungai bergoyang perlahan, diayun oleh belaian angin malam yang sepoi-sepoi. "
        f"Kupu-kupu malam beristirahat di balik daun talas yang lebar, menikmati ketenangan malam yang sunyi. "
        f"Bintang-bintang di permukaan telaga ikut beristirahat bersama ayunan gelombang kecil yang tenang. "
        f"Seluruh alam raya seolah sedang berbisik bersama, 'Shhh... Waktunya tidur... Waktunya beristirahat...' "
        f"Kelopak matamu kini terasa begitu berat... Kamu merasa sangat mengantuk, tenang, dan tenteram... "
        f"Tubuhmu semakin rileks, meleleh nyaman ke dalam kelembutan kasur dan bantalmu yang empuk. "
        f"Napasmu tenang... hembusan napasmu lembut dan sangat teratur... "
        f"Jantungmu berdetak damai, seirama dengan ketenangan malam yang sunyi dan teduh. "
        f"Semua otot di badanmu melepaskan kepalan, beristirahat total tanpa ada beban sedikit pun. "
        f"Kamu aman di sini, di bawah penjagaan lentera malam yang hangat dan penuh cinta. "
        f"Pejamkan matamu dengan sempurna, sahabat cilik... Hanyutlah ke dalam mimpi yang paling damai. "
        f"Selamat tidur nyenyak, si kecil {name}... Selamat malam... Mimpi indah selalu..."
    )

def _toddler_kejora_id(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"Langit malam terbentang luas bagai tirai sutra biru pekat yang dihiasi permata berkilauan... "
        f"Si kecil {name} telah berbaring nyaman di bawah selimut hangatnya yang beraroma harum dan segar. "
        f"Tarik napas panjang yang tenang... rasakan udara malam yang damai memenuhi dadamu... "
        f"lalu hembuskan perlahan-lahan... membiarkan rasa santai mengalir ke seluruh jemari tangan dan kakimu... "
        f"Di langit timur yang tinggi, Bintang Kejora bersinar paling terang dengan cahaya perak yang sangat ramah dan menyejukkan. "
        f"Cahaya Bintang Kejora turun perlahan bagai jembatan selendang sutra yang turun menyapa kamarmu. "
        f"Di atas selendang cahaya itu, si kecil {name} diajak berbaring melayang santai di antara awan-awan perak yang empuk. "
        f"Bintang Kejora memancarkan kehangatan yang membuat seluruh otot tubuhmu terasa lemas, santai, dan rileks. "
        f"Bulan perak menemani di sampingmu, tersenyum dengan tatapan penuh perlindungan dan kasih sayang. "
        f"Bintang Kejora berbisik dengan suara selembut hembusan angin malam yang menyejukkan, "
        f"'Selamat malam, permata hatiku {name}... Seluruh galaksi dan bintang-bintang menjaga tidurmu dalam cinta dan {lesson}.' "
        f"Bintang-bintang kecil di sekelilingmu mulai menari pelan, berputar membentuk lingkaran tidur yang menenangkan jiwa. "
        f"Komet-komet kecil meluncur pelan tanpa suara di kejauhan, menaburkan debu mimpi yang berkilauan keemasan. "
        f"Awan-awan galaksi yang berwarna ungu lembut berarak perlahan menutupi cakrawala, menyelimuti angkasa dengan kehangatan. "
        f"Bintang-bintang pemalu memejamkan mata mereka satu per satu di balik kabut malam yang damai. "
        f"Satu per satu bintang meredupkan kerlipnya, berganti menjadi pendar cahaya lembut yang menidurkanmu dengan damai. "
        f"Dunia di bawah sana telah hening dan terlelap dalam kegelapan malam yang damai dan tenteram. "
        f"Pohon-pohon di bumi telah tertidur, hewan-hewan malam telah meringkuk di sarang masing-masing. "
        f"Desir angin angkasa membunyikan lonceng perak nirwana yang berdenting sangat halus... ning... nang... nong... "
        f"Kabut malam yang hangat merangkul tubuhmu laksana gendongan yang paling nyaman di seluruh dunia. "
        f"Selimut tidurmu menjaga setiap inci tubuh mungilmu tetap hangat, tenang, dan terlindungi. "
        f"Kelopak matamu kini terasa semakin berat... Shhh... Rasakan ketenangan yang merayap ke seluruh pikiranmu... "
        f"Napasmu mengalir lambat... teratur... dan begitu nyaman... "
        f"Pundakmu rileks, lehermu nyaman di atas bantal, dan kedua tanganmu beristirahat tenang. "
        f"Semua beban dan rasa lelah telah menguap ke angkasa malam yang luas dan bebas. "
        f"Bantalmu yang empuk menopang kepalamu dengan penuh kelembutan dan rasa sayang yang tulus. "
        f"Kamu adalah anak yang sangat istimewa, sangat dicintai, dan selalu diberkati dengan kedamaian. "
        f"Tutup matamu rapat-rapat, sayangku... Biarkan pendar Bintang Kejora mengiringi tidurmu yang paling lelap. "
        f"Selamat tidur nyenyak, {name}... Selamat malam... Istirahatlah dalam dekap semesta..."
    )

# ==============================================================================
# 2. BAHASA INDONESIA: OLDER KIDS (Age 4-8) Target: 660 - 750 words
# ==============================================================================

def _older_pinisi_id(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"Langit senja di ufuk barat perlahan-lahan memudar, berganti menjadi bentangan kain beludru biru pekat bertabur sejuta permata bintang yang berkelip hening. "
        f"{name} yang berusia {age} tahun berbaring nyaman di bawah selimut hangat, merasakan detak jantung dan tarikan napas yang mulai melambat dengan sangat tenang. "
        f"Tarik napas panjang dan dalam... rasakan ketenangan malam mengisi setiap sudut pikiranmu yang cerdas... lalu hembuskan perlahan-lahan ke udara bebas. "
        f"Biarkan seluruh kepenatan setelah seharian belajar dan beraktivitas mengalir keluar dari tubuhmu bersama setiap hembusan napas yang damai. "
        f"Malam ini, kamarmu adalah tempat yang paling aman, paling nyaman, dan paling tenang di seluruh dunia. "
        f"Pintu imajinasimu terbuka lebar menuju sebuah teluk rahasia di pesisir Nusantara, di mana sebuah perahu pinisi megah bernama Pusaka Bintang sedang berlabuh tenang di atas air laut yang bening bagai kaca cermin. "
        f"Layar-layar pinisi itu terbuat dari tenunan benang sutra perak yang menangkap cahaya rembulan, mengembang lembut tanpa mengeluarkan suara sedikit pun. "
        f"Kayu ulin dan cendana pada lambung kapal menguapkan aroma wangi rempah yang menenangkan, berpadu serasi dengan kesegaran angin laut malam. "
        f"Saat {name} melangkah ke atas dek kayu yang bersih, Nakhoda Bijak menyambut dengan sebuah senyuman teduh dan binar mata yang ramah. "
        f"'Selamat datang di pelayaran malam, penjelajah hebat {name},' sapanya lirih dalam nada suara yang menenangkan kalbu. "
        f"'Malam ini, kita berlayar melintasi Samudra Damai menuju Kepulauan {theme}, di mana rahasia {lesson} akan membimbing setiap impianmu.' "
        f"Perahu pinisi meluncur anggun membelah ombak-ombak kecil yang berkilauan bagai taburan berlian. "
        f"Di bawah permukaan air yang jernih, ribuan ubur-ubur bercahaya keemasan menari pelan, menerangi jalan setapak di dasar laut yang sunyi. "
        f"Ikan-ikan lumba-lumba melompat anggun berpasangan di sisi lambung kapal, menemani di sampingmu bagai sahabat lama yang setia tanpa memercikkan air ke dek kapal. "
        f"Di kejauhan, gugusan Bintang Pari bersinar megah di langit selatan, menjadi kompas abadi yang membimbing setiap pelaut yang memiliki ketulusan hati dan budi pekerti luhur. "
        f"Nakhoda menunjuk ke arah haluan perahu yang mengarah ke pulau tidur. "
        f"'Ketahuilah, {name}, bahwa ombak samudra yang paling dahsyat sekalipun pada akhirnya akan kembali tenang dan bersandar damai di tepian pantai pasir putih. "
        f"Begitu pula dengan harimu... apa pun tantangan yang telah kamu hadapi hari ini, malam ini adalah saat istimewa untuk memulihkan seluruh energimu dengan penuh {lesson}.' "
        f"Dan tepat ketika ia berbicara, sebuah lentera perunggu mungil berkelip lembut di tiang layar utama, memancarkan cahaya jingga hangat yang meresap ke dalam lubuk hati {name}. "
        f"Di dek depan, seorang musafir malam memainkan alat musik gambus petik dengan petikan dawai yang sangat lambat, mengalun indah mengiringi keheningan lautan. "
        f"Kini semilir angin laut berhembus semakin pelan... semakin sepoi-sepoi... Layar perahu mulai dikuncupkan perlahan oleh para pelaut malam yang bergerak tanpa suara. "
        f"Laju perahu pinisi melambat dengan sangat halus, mengapung tenang di tengah laguna berair tenang yang terlindung oleh bukit karang. "
        f"Lumba-lumba menyelam perlahan ke balik terumbu karang yang sunyi, memejamkan mata mereka dengan damai dalam lindungan malam yang sejuk. "
        f"Nakhoda membimbing {name} menuju kabin istirahat di geladak perahu, menyelimutimu dengan selimut tenun sutra hangat yang luar biasa ringan, lembut, dan nyaman. "
        f"Dengarkan irama ombak yang berbisik lembut di lambung kayu perahu... Gesekan ombak yang ritmis... berayun maju... lalu berayun mundur... berayun perlahan... begitu menenangkan... begitu syahdu dan damai. "
        f"Rasakan gelombang relaksasi merayap naik dari ujung jemari kakimu, naik ke betis, lutut, dan paha... melepaskan semua kelelahan ototmu. "
        f"Punggung dan bahumu kini bersandar bebas, lehermu terasa ringan, dan rahangmu rileks sepenuhnya. "
        f"Kelopak matamu kini terasa semakin berat... Shhh... Sangat berat dan mengantuk... "
        f"Pikiranmu melayang bebas dan tenang... Mengikuti aliran ketenangan samudra yang membawamu menuju tidur yang paling lelap dan menyegarkan. "
        f"Setiap tarikan napas membawamu lebih dalam ke dalam ketenteraman... Setiap hembusan napas menyingkirkan segala sisa pikiran hari ini. "
        f"Petualangan hebatmu hari ini telah selesai dengan sempurna... Semua cita-cita, ide cerdas, dan kebaikanmu tersimpan rapi di dalam dekapan semesta. "
        f"Dan esok pagi, fajar baru akan menyambutmu dengan sinar matahari cerah serta harapan-harapan baru yang menanti untuk dijelajahi. "
        f"Tidurlah dengan damai dan tenang, wahai {name}... Seluruh bintang di samudra malam ini selalu menjagamu dalam kehangatan cinta. "
        f"Selamat tidur... Selamat malam... Mimpi indah..."
    )

def _older_kalpataru_id(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"Semilir angin malam bertiup pelan melintasi pucuk-pucuk pepohonan purba, membawa aroma harum bunga kenanga, melati hutan, dan keharuman tanah basah sehabis hujan rintik senja. "
        f"{name} yang berusia {age} tahun menarik selimut hangat hingga ke dagu, merasakan kenyamanan dan rasa aman yang begitu sempurna di atas tempat tidurnya. "
        f"Tarik napas dalam-dalam secara perlahan... rasakan kesejukan yang menentramkan jiwa masuk memenuhi rongga dadamu... lalu hembuskan perlahan-lahan, membiarkan kedua pundakmu turun dan rileks sepenuhnya. "
        f"Lepaskan segala ketegangan pikiran, membiarkan keheningan malam membimbingmu menuju kedamaian sejati yang telah lama kamu rindukan. "
        f"Di perbatasan antara alam nyata dan dunia imajinasi, terbentang luas Hutan Kalpataru... hutan keramat Nusantara yang dipenuhi pepohonan purba yang bijaksana dan kedamaian abadi. "
        f"Ketika melintasi jalan setapak beralaskan lumut hijau zamrud yang empuk bagai karpet permadani istana, {name} melihat sebatang pohon raksasa yang batangnya memancarkan pendar cahaya keperakan yang menyejukkan hati. "
        f"Itulah Pohon Hayat Kalpataru, tempat di mana seluruh alam semesta menitipkan rahasia ketenangan dan ketenteraman malam. "
        f"Dedaunan pohon itu berdesir pelan laksana dawai kecapi kuno yang melagukan senandung tidur pengantar istirahat bagi seluruh penghuni rimba. "
        f"Akar-akar besarnya yang kokoh memeluk bumi dengan lembut, mengalirkan rasa aman yang tak tergoyahkan ke dalam hati setiap musafir. "
        f"Dari balik rerimbunan tanaman pakis purba yang rindang, melangkah keluar Sahabat Kancil yang berbulu keemasan, didampingi oleh seekor Rusa bertanduk mutiara bercahaya lembut. "
        f"'Selamat malam sahabatku, {name},' bisik Kancil dengan suara yang begitu berwibawa namun teduh menenangkan jiwa. "
        f"'Kami telah lama menantikan seorang penjelajah berhati murni yang membawa nilai-nilai {lesson} dan ketulusan jiwa sepertimu.' "
        f"Rusa bertanduk mutiara membimbing {name} menuju mata air kristal di bawah naungan akar pohon Kalpataru yang kokoh, di mana air pegunungan mengalir jernih tanpa riak yang tergesa-gesa. "
        f"Di atas dahan-dahan pohon yang menjulang tinggi, ratusan Burung Cendrawasih tertidur pulas dengan kepala terselip rapi di bawah sayap keemasan mereka yang berkilauan. "
        f"Kancil yang bijak menatap {name} dengan senyum penuh kehangatan. 'Ketahuilah, {name}, bahwa kehebatan sejati dalam hidup ini bukanlah diukur dari seberapa cepat kamu berlari, melainkan dari kedamaian hati yang mampu memancarkan {lesson} kepada setiap makhluk di sekitarmu.' "
        f"Petuah yang bijaksana itu meresap ke dalam dada {name}, bagai kehangatan secangkir madu yang menenangkan seluruh jiwa ragamu. "
        f"Kancil menyerahkan sebuah biji pohon bersinar redup sebagai tanda persahabatan, yang kamu simpan dalam saku pakaianmu dengan rasa syukur yang mendalam. "
        f"Dari kejauhan, alunan gamelan bambu yang dimainkan oleh para peri hutan terdengar sayup-sayup... nadanya lambat, lembut, dan mengayun jiwa ke alam ketenteraman. "
        f"Kini seluruh penghuni rimba telah kembali ke sarang mereka masing-masing untuk menikmati istirahat malam yang panjang dan damai. "
        f"Kelinci-kelinci hutan meringkuk damai di dalam liang tanah yang hangat... Burung hantu malam menutup matanya yang bijaksana di lubang pohon kuno. "
        f"Gajah-gajah kecil tidur bersandar pada induknya di padang rumput yang sunyi, mendengkur halus dalam mimpi damai tanpa rasa takut. "
        f"Suara jangkrik malam dan gemersik dedaunan terdengar semakin jauh... semakin lembut... dan semakin ritmis... seolah meninabobokan seluruh isi bumi. "
        f"Dengarkan desau angin malam yang melintasi dedaunan rimbun... Shhh... Tenang sekali... Begitu damai dan tenteram... "
        f"Kelopak matamu terasa semakin berat... tak tertahankan lagi oleh rasa kantuk yang begitu manis dan menenteramkan jiwa. "
        f"Rasakan gelombang kehangatan relaksasi merayap perlahan dari ujung jari-jari kakimu... "
        f"merambat naik ke pergelangan kaki, betis, lutut, dan seluruh paha... melepaskan segala sisa ketegangan otot melangkah seharian ini. "
        f"Perut dan dadamu kini bernapas dengan sangat ringan dan teratur... "
        f"Punggungmu tenggelam nyaman ke dalam kasur, bahumu turun santai, dan kedua lenganmu beristirahat lemas di sisi tubuhmu. "
        f"Lehermu terasa ringan, rahangmu melemas tanpa kertakan gigi, keningmu halus dan sejuk, dan kedua kelopak matamu menutup dengan sangat nyaman dan santai. "
        f"Hutan Kalpataru merangkulmu dalam kehangatan perlindungan malam yang abadi dan penuh kasih sayang. "
        f"Bintang-bintang di sela dedaunan kanopi mengedipkan salam tidur yang menyejukkan batinmu. Selimutmu yang tebal dan hangat merangkul tubuhmu dalam rasa aman yang tak tergoyahkan. "
        f"Segala lelah hari ini telah sirna, berganti dengan ketenangan jiwa yang mendalam dan damai. "
        f"Tidurlah dengan nyenyak, wahai {name}... Esok hari akan membentangkan lembaran baru yang penuh keajaiban, tawa riang, dan keberhasilan. Selamat tidur dan selamat malam..."
    )

def _older_awan_id(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"Kabut tipis beraroma sedap malam dan teh melati perlahan-lahan turun memeluk lereng-lereng perbukitan hijau zamrud yang sunyi. "
        f"{name} yang berusia {age} tahun merebahkan tubuhnya di atas kasur yang empuk, menikmati ketenangan malam yang merayap turun dengan lembut dan menyejukkan. "
        f"Tarik napas yang dalam dan tenang... rasakan udara sejuk pegunungan mengisi seluruh rongga dadamu... lalu hembuskan dengan penuh kelegaan dan kenyamanan yang mendalam. "
        f"Biarkan ketegangan seharian menguap ke udara malam yang sejuk, menyisakan tubuh yang santai dan pikiran yang hening tanpa beban. "
        f"Di hadapan pandangan batinmu, hamparan kebun teh yang luas membentang di bawah kubah langit malam negeri {theme} yang bertabur jutaan bintang berkilauan. "
        f"Di lembah yang sunyi ini, semilir angin malam membawa alunan seruling bambu yang terdengar begitu syahdu dari kejauhan, menuntun langkahmu menuju tangga awan perak yang megah. "
        f"Setiap anak tangga terbuat dari gumpalan awan kapas yang hangat, padat, dan memantulkan pendar cahaya rembulan yang keemasan. "
        f"Langkah kakimu terasa seringan bulu angsa saat menaiki tangga awan itu, ditemani kunang-kunang langit yang beterbangan tenang. "
        f"Di puncak perbukitan awan yang tinggi, seorang Penjaga Angin dengan jubah sutra bertabur ornamen bintang kejora menyambut kedatanganmu dengan anggukan ramah penuh hormat. "
        f"'Selamat datang di istana kedamaian Negeri di Atas Awan, {name},' ucapnya dengan suara berat dan teduh yang menenangkan sukma. "
        f"'Malam ini, seluruh langit berterima kasih atas ketenangan jiwa, kerja keras, dan {lesson} yang telah kamu tunjukkan hari ini.' "
        f"Dari atas mahkota awan ini, seluruh bumi tampak tertidur pulas dalam pelukan selimut malam yang tenteram. "
        f"Lampu-lampu kota dan desa di dataran rendah berkelip redup bagai kunang-kunang yang perlahan-lahan terlelap tidur. "
        f"Penjaga Angin mengulurkan sebuah cangkir tembikar berisi teh chamomile hangat beraroma madu hutan, menghangatkan kedua telapak tangan {name}. "
        f"'Ingatlah selalu,' bisiknya penuh kebijaksanaan, 'bahkan badai yang paling dahsyat sekalipun pada akhirnya akan tunduk pada keheningan jiwa yang dipenuhi ketenangan dan {lesson}.' "
        f"Pemandangan lembah dari atas awan ini sungguh memesona... Danau-danau di bawah sana tampak bagai cermin perak yang memantulkan rasi bintang. "
        f"Paviliun awan di sekitarmu terhiasi lentera kristal yang meredup pelan, menyesuaikan dengan irama matamu yang mulai mengantuk. "
        f"Bunga-bunga edelweis langit mekar tanpa suara, menebarkan wangi kesucian yang membuai alam pikiranmu menjadi sangat rileks. "
        f"Gumpalan awan-awan di sekelilingmu mulai merapat secara perlahan, membentuk peraduan raksasa yang paling empuk dan hangat di seluruh jagat raya. "
        f"Lonceng-lonceng angin di bubungan atap istana awan berdenting lirih... klinting... klinting... menyenandungkan tidur yang tenteram. Di sekeliling paviliun, taman bunga langit bermekaran dengan kelopak berhiaskan embun perak yang berkilau lembut. Aroma madu manis dan bunga sedap malam melayang tenang di udara sejuk, membelai indra penciumanmu dengan kelembutan yang memabukkan rasa kantuk. Penjaga Angin menuangkan setetes sari embun penenang ke dalam cangkirmu, membuat setiap tegukan teh chamomile terasa bagai ramuan mimpi paling damai. Lembah di bawah sana kini benar-benar senyap, dibungkus tirai kabut putih yang tebal dan hening. Udara sejuk malam menyelimuti setiap sudut ruanganmu dengan kesegaran yang menenangkan seluruh jiwa ragamu. "
        f"Bintang-bintang kejora meredupkan cahaya terangnya satu demi satu, memberikan ruang bagi keheningan malam yang menenangkan untuk membuai tidurmu. "
        f"Dengarkan desau semilir angin semesta yang syahdu... Shhh... Begitu hening... Sangat tenang sekarang... "
        f"Kelopak matamu terasa sangat berat... rasa kantuk yang menyejukkan mengalir ke setiap pembuluh darahmu. "
        f"Rasakan gelombang kehangatan relaksasi merayap perlahan dari ujung jari-jari kakimu... "
        f"merambat naik ke pergelangan kaki, betis, lutut, dan seluruh paha... melepaskan segala sisa ketegangan otot. "
        f"Perut dan dadamu kini bernapas dengan sangat ringan dan teratur... "
        f"Punggungmu tenggelam nyaman ke dalam kasur, bahumu turun santai, dan kedua lenganmu beristirahat lemas di sisi tubuhmu. "
        f"Lehermu terasa ringan, rahangmu melemas tanpa kertakan gigi, keningmu halus dan sejuk, dan kedua kelopak matamu menutup dengan sangat nyaman dan santai. "
        f"Napasmu menjadi sangat santai, lambat, dalam, dan teratur... Tubuhmu seolah melayang ringan di atas buaian awan mimpi. "
        f"Kamu aman, kamu terlindungi, dan kamu begitu dikasihi oleh semesta raya. "
        f"Biarkan segala pikiranmu beristirahat dan melayang bebas menuju alam mimpi yang indah dan membahagiakan. "
        f"Tidurlah dengan lelap, {name}... Bintang kejora akan selalu berjaga di atas kepalamu hingga fajar tiba. Selamat tidur nyenyak dan selamat malam..."
    )

def _older_kunang_id(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"Lembah sungai purba yang sunyi perlahan-lahan tenggelam dalam kehangatan malam yang hening dan syahdu. "
        f"{name} yang berusia {age} tahun berbaring santai di atas kasur yang empuk, merasakan detak jantung dan ritme napas yang melambat dengan sangat damai. "
        f"Tarik napas panjang yang menenangkan... rasakan hawa malam yang bersih memenuhi rongga dadamu... lalu hembuskan perlahan-lahan, melepaskan segala ketegangan hari ini. "
        f"Biarkan kepenatan pikiranmu hanyut perlahan bersama hembusan napas yang panjang dan lega ke pelukan malam yang ramah. "
        f"Di hadapan alam imajinasimu, terbentang Lembah Kunang-Kunang... sebuah lembah tersembunyi di mana sungai kristal mengalir tenang tanpa gelombang di antara rimbunnya hutan bambu. "
        f"Saat malam menyentuh titik paling sunyi, jutaan lentera kunang-kunang emas mulai menyala serempak di sepanjang tebing sungai, memancarkan cahaya hangat bagai ribuan bintang jatuh yang hinggap di bumi. "
        f"Si kecil {name} melangkah di atas jembatan kayu terapung yang kokoh, disambut oleh seekor Rusa Emas bercahaya yang berdiri tenang di tepian dermaga bambu. "
        f"'Selamat malam, penjelajah muda {name},' sapa Rusa Emas dengan nada suara yang hangat bagai perapian di musim dingin. "
        f"'Malam ini, lembah lentera ini mempersembahkan cahayanya untuk merayakan keteguhan hati dan {lesson} yang kamu miliki.' "
        f"Rusa Emas membimbingmu menaiki sebuah rakit kayu cendana kecil yang meluncur tenang mengikuti arus sungai yang lembut. "
        f"Di atas permukaan air yang jernih bagai cermin, pantulan cahaya lentera kunang-kunang bergoyang lembut seirama dengan riak air yang lambat. "
        f"Pohon-pohon beringin tua di tepi sungai merundukkan ranting-rantingnya, menyaring angin malam menjadi bisikan suara yang meninabobokan siapa pun yang mendengarnya. "
        f"Kincir air bambu tua di tepi dermaga berputar perlahan dengan irama lembut... kresek... krik... air mengalir menyejukkan jiwa. "
        f"Rusa Emas menatap lentera bintang di ujung rakit dan berbisik lembut, 'Kekuatan terbesar manusia tidak terletak pada seberapa keras ia berteriak, melainkan pada ketenangan batin yang memancarkan kejujuran dan {lesson} di dalam kegelapan.' "
        f"Kata-kata itu memberikan kelegaan luar biasa di dalam pikiran {name}, membuat seluruh persendian tubuhmu terasa lemas, santai, dan nyaman. "
        f"Rusa Emas memberikan sebuah lentera bambu kecil yang menyala temaram, menghangatkan dekapan kedua tanganmu. "
        f"Seorang peniup seruling buluh di atas perahu nelayan tua meniupkan melodi malam yang syahdu... suaranya mengalun pelan terbawa angin sungai yang sejuk. Ratusan capung malam hinggap damai di atas tangkai-tangkai bunga teratai, memejamkan mata dalam keheningan kolam. Pohon-pohon pandan wangi di tepian rawa menghembuskan keharuman segar yang membersihkan seluruh beban pikiranmu dari seharian beraktivitas. Rusa Emas mengusapkan hidungnya yang hangat ke punggung tanganmu dengan penuh kasih sayang, membisikkan bahwa seluruh alam raya senantiasa menjagamu dengan ketulusan. Air telaga yang tenang memantulkan jutaan lentera kuning keemasan, menciptakan lukisan mimpi yang paling damai di muka bumi. Kehangatan selimutmu terasa begitu sempurna melindungi tubuhmu dari embun malam yang sejuk. "
        f"Kini rakit telah berlabuh damai di sebuah telaga teratai yang sunyi... Bunga-bunga teratai putih telah mengatupkan kelopaknya dengan anggun untuk tidur. "
        f"Lentera kunang-kunang mulai meredupkan sinarnya secara bertahap, berganti menjadi temaram hangat yang memanggil rasa kantuk yang mendalam. "
        f"Bebek-bebek liar telah menyembunyikan kepalanya di balik bulu tebal di pulau kecil di tengah telaga. "
        f"Angin malam berbisik lirih melalui sela rumpun bambu... Suara gemerisik daunnya terdengar ritmis... mengalun lembut... Shhh... Istirahatlah sekarang... Semuanya aman dan tenteram... "
        f"Kelopak matamu terasa sangat berat untuk dibuka kembali... Otot-otot leher, pundak, dan punggungmu melepas semua lelah. "
        f"Rasakan gelombang kehangatan relaksasi merayap perlahan dari ujung jari-jari kakimu... "
        f"merambat naik ke pergelangan kaki, betis, lutut, dan seluruh paha... melepaskan segala sisa ketegangan otot. "
        f"Perut dan dadamu kini bernapas dengan sangat ringan dan teratur... "
        f"Punggungmu tenggelam nyaman ke dalam kasur, bahumu turun santai, dan kedua lenganmu beristirahat lemas di sisi tubuhmu. "
        f"Lehermu terasa ringan, rahangmu melemas tanpa kertakan gigi, keningmu halus dan sejuk, dan kedua kelopak matamu menutup dengan sangat nyaman dan santai. "
        f"Irama detak jantungmu selaras dengan desau lembut sungai yang mengalir tenang tanpa henti... "
        f"Napasmu mengalir pelan, dalam, dan teratur... Hanyutlah dalam arus ketenangan yang abadi. "
        f"Hari esok akan datang dengan limpahan fajar baru yang gemilang dan peluang-peluang emas yang menunggu langkahmu. "
        f"Tidurlah dengan nyenyak, {name}... Cahaya lentera lembah akan selalu menerangi jalan mimpimu yang indah. Selamat malam..."
    )

def _older_kejora_id(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"Langit angkasa raya terbentang tanpa batas, memamerkan keindahan galaksi spiral dan debu bintang yang berpendar bagai permata di atas permadani sutra hitam. "
        "{name} yang berusia {age} tahun merebahkan kepala dengan nyaman di atas bantal yang empuk, merasakan sensasi rileks yang mengalir dari ujung kepala hingga ujung jari kakinya. "
        f"Tarik napas panjang dan tenang... rasakan ketenangan kosmos yang luas dan hening mengalir ke dalam jiwamu... lalu lepaskan napasmu secara perlahan, membiarkan tubuhmu tenggelam semakin dalam ke kasur. "
        f"Keluaran napas yang panjang membawa serta seluruh ketegangan hari ini, menyisakan ketenangan batin yang murni dan damai. "
        f"Di alam mimpimu malam ini, sebuah kubah observatorium kristal berdiri megah di puncak Gunung Kejora, menghadap langsung ke arah cakrawala bintang yang memukau di langit {theme}. "
        f"Di tengah kubah kristal itu, Bintang Kejora bersinar dengan keanggunan luar biasa, memancarkan spektrum cahaya perak dan biru safir yang hangat dan menyejukkan. "
        f"Seorang Pengelana Antariksa yang bijaksana dengan jubah tenun konstelasi bintang menyambut {name} dengan senyum bersahabat yang penuh keteduhan. "
        f"'Selamat datang di anjungan bintang malam, sahabat hebat {name},' tuturnya dengan suara yang bergema lembut dan menentramkan batin. "
        f"'Malam ini, konstelasi semesta berkumpul untuk mencatat semua langkah kebaikan dan {lesson} yang telah kamu ukir di bumi.' "
        f"Pengelana Bintang mengajak {name} duduk di atas kursi terapung yang terbuat dari gumpalan awan kosmik yang luar biasa empuk. "
        f"Melalui jendela kubah kristal, planet-planet berputar lambat dalam orbitnya masing-masing tanpa ada benturan, bergerak dalam harmoni sempurna yang menenangkan pikiran. "
        f"Cincin Saturnus yang keemasan berputar anggun bagai piringan musik yang memainkan simfoni keheningan abadi. "
        f"Bulan sabit tampak melayang anggun di dekat jendela, memancarkan cahaya perak sejuk yang membelai pipimu. "
        f"Pengelana Bintang menatap ke dalam matamu yang mulai mengantuk, lalu berbisik penuh makna, 'Bintang yang paling terang sekalipun selalu membutuhkan kegelapan malam untuk memperlihatkan keindahannya. Istirahatmu malam ini adalah awal dari kekuatan terbesarmu esok hari, yang senantiasa dipandu oleh {lesson}.' "
        f"Kehangatan cahaya kosmik meresap ke dalam dada {name}, menyingkirkan segala sisa keraguan, kepenatan, dan kegelisahan. "
        f"Tirai angkasa yang dipenuhi debu nebula berpendar lembut, memberikan rasa nyaman yang mendalam ke seluruh pikiranmu. "
        f"Genta kosmis kristal berdentang pelan di sudut observatorium... dung... mengalunkan frekuensi tidur yang menenangkan seluruh sel tubuhmu. Peta-peta bintang kuno yang terlukis di dinding kubah memancarkan pendar keemasan, memperlihatkan rasi Bintang Pari dan Bintang Waluku yang menjaga malam Nusantara. Pengelana Antariksa menyelimutimu dengan kain tenun kosmik beraroma melati perak yang sangat hangat dan ringan laksana udara hampa. Di luar kubah, jutaan debu komet melayang tenang bagai kunang-kunang antariksa yang sedang bersiap untuk tidur lelap. Seluruh galaksi seakan sedang menarik napas panjang bersamamu, menyanyikan simfoni keheningan yang tak berujung. Cahaya bintang yang ramah menghangatkan hati dan jiwamu dalam kedamaian malam yang abadi. "
        f"Kini musik semesta yang hening mulai mereda... Komet-komet malam meluncur tenang dan menghilang di balik batas galaksi. "
        f"Lampu-lampu kubah kristal meredup secara otomatis, menyisakan pendar Bintang Kejora yang lembut bagai lampu tidur yang menenangkan. "
        f"Dengarkan detak waktu semesta yang damai... Shhh... Suasana begitu syahdu... Benar-benar hening dan tenang... "
        f"Kelopak matamu terasa luar biasa berat... Kamu merasa sangat mengantuk dan tenteram di bawah naungan semesta yang maha luas. "
        f"Rasakan gelombang kehangatan relaksasi merayap perlahan dari ujung jari-jari kakimu... "
        f"merambat naik ke pergelangan kaki, betis, lutut, dan seluruh paha... melepaskan segala sisa ketegangan otot. "
        f"Perut dan dadamu kini bernapas dengan sangat ringan dan teratur... "
        f"Punggungmu tenggelam nyaman ke dalam kasur, bahumu turun santai, dan kedua lenganmu beristirahat lemas di sisi tubuhmu. "
        f"Lehermu terasa ringan, rahangmu melemas tanpa kertakan gigi, keningmu halus dan sejuk, dan kedua kelopak matamu menutup dengan sangat nyaman dan santai. "
        f"Sensasi gravitasi bumi yang lembut membuai setiap sendi tubuhmu dalam kenyamanan yang tiada tara... "
        f"Detak jantungmu teratur dan lambat... Tarikan napasmu mengalir tenang, menyatu dengan kedamaian malam yang tak bertepi. "
        f"Kamu adalah bagian yang sangat berharga dari alam semesta ini, dilindungi oleh doa dan cinta yang tulus selamanya. "
        f"Pejamkan matamu, penjelajah bintang... Biarkan gravitasi tidur yang manis membawamu meluncur ke dalam mimpi terindah. "
        f"Tidurlah dengan lelap, {name}... Bintang Kejora akan selalu menemanimu hingga fajar menyingsing. Selamat tidur dan selamat malam..."
    )

# ==============================================================================
# 3. ENGLISH: TODDLER (Age <= 3) Target: 380 - 450 words
# ==============================================================================

def _toddler_pinisi_en(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"Night has gently settled over the quiet, peaceful seashore... "
        f"A soft sea breeze drifts across the waters, lightly brushing the cheek of little {name}. "
        f"Take a slow, deep breath in... feeling the cool, clean night air fill your chest... "
        f"and let it gently float out with a calm, comfortable sigh... "
        f"Your little body feels so warm, so relaxed, and so safe tonight beneath the soft covers. "
        f"Resting beside the calm white sandy shore is a charming little wooden pinisi boat, hand-carved with fragrant jasmine blossoms. "
        f"Inside the boat are plush velvet cushions and a woven blanket as soft as morning mist. "
        f"The round silver moon smiles down kindly from the deep blue sky, casting a path of sparkling moonlight across the calm waters. "
        f"Little {name} steps carefully inside the boat, snuggling down with your favorite toy under the shelter of the bamboo canopy. "
        f"The little pinisi boat begins to rock gently... rocking to the left... and rocking to the right... "
        f"Moving with the soothing, rhythmic whisper of the gentle harbor waves. "
        f"All around the boat, the water glows softly with tiny golden reflections, like shimmering stars resting on the surface. "
        f"This is the peaceful light of the calm bay of {theme}, quiet and comforting. "
        f"A gentle little sea turtle with an emerald shell glides smoothly beside the boat. "
        f"The sea turtle looks up with sleepy, kind eyes and whispers softly, "
        f"'Goodnight, sweet {name}... The great peaceful ocean will keep you safe tonight in warmth and {lesson}.' "
        f"High above, friendly constellations twinkle like nightlights, watching over your slumber. "
        f"The little colorful fish have folded their fins, resting safely among the swaying green seagrass. "
        f"The sleepy sea birds have tucked their heads under their wings upon the sturdy mangrove branches. "
        f"Everything around you is becoming so quiet... Shhh... Calm and peaceful now... "
        f"Your eyelids are growing heavier and heavier... so pleasantly sleepy... "
        f"Your breathing is becoming slow, steady, and light, like the gentle lapping of the sea. "
        f"Every breath lets go of the day's play... Your arms and legs are completely relaxed. "
        f"You are safe, you are deeply loved by all your family, and you are wonderfully made. "
        f"Close your eyes, little voyager... Let the pinisi boat carry you toward the sweetest dreams. "
        f"Sleep tight in the embrace of this gentle night... "
        f"Goodnight, sweet {name}... Goodnight... Sweet dreams..."
    )

def _toddler_kalpataru_en(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"Night has descended gracefully over the lush, ancient tropical forest... "
        f"In your cozy bedroom, little {name} is getting ready for peaceful dreams. "
        f"Take a slow, gentle breath in... letting the stillness of the evening fill your heart... "
        f"and breathe out softly... letting go of all the day's excitement with a warm sigh... "
        f"Feel how soft and cozy your bed and pillow are tonight... You are safe, you are peaceful. "
        f"Deep within the quiet heart of nature stands the sacred Kalpataru Tree, ancient and full of wonder. "
        f"Its broad leaves glow with a warm emerald light that soothes and relaxes the eyes. "
        f"Beneath the sheltered branches of this loving tree, little woodland friends are curling up to sleep. "
        f"Little {name} rests upon a thick carpet of soft green forest moss, clean, cool, and fragrant. "
        f"A wise little mouse deer, Kancil, rests his head gently near your feet, curling into a cozy ball. "
        f"A beautiful golden Bird of Paradise perches quietly upon a sturdy branch above, humming a soft bedtime melody. "
        f"Kancil looks up at {name} with warm, affectionate eyes and whispers softly, "
        f"'Sleep soundly, sweet {name}... Today you brought so many smiles and so much {lesson} to our world.' "
        f"The night breeze drifts through the treetops, carrying the sweet perfume of wild jasmine and orchids. "
        f"Tiny dewdrops fall gently from the leaves... Drip... drop... so rhythmic, so calming, so relaxing. "
        f"All the creatures of the woods have closed their eyes in quiet harmony. "
        f"The little forest deer are fast asleep behind the bamboo grove that sways in the night wind. "
        f"The baby squirrels have tucked their fluffy tails around their noses inside their warm hollow nests. "
        f"Night butterflies have settled peacefully on sleeping flower petals without a sound. "
        f"Soft crickets whisper their gentle evening lullaby into the quiet air... "
        f"Your little body feels warmer and more relaxed, sinking softly into the hug of your bed. "
        f"Listen to the rustle of the leaves... Shhh... Rest now... Everything is safe and still... "
        f"Your eyelids are so heavy... no need to open them again... "
        f"Your breath is steady, gentle, and quiet, like a soft breeze. "
        f"Your shoulders and hands are completely at rest on the blankets. "
        f"You are a precious treasure, deeply loved and protected always. "
        f"Close your eyes, little friend... Let the magic of the woods guide you to restful sleep. "
        f"Goodnight, sweet {name}... Goodnight... Rest peacefully..."
    )

def _toddler_awan_en(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"Night has arrived, wrapping the rolling mountain hills in a soft blanket of white mist... "
        f"Little {name} rests comfortably in bed, gazing up at the quiet evening sky filled with stars. "
        f"Take a slow, deep breath in... feeling the fresh mountain air scented with sweet tea blossoms... "
        f"and gently breathe out... letting your whole body become light and wonderfully relaxed... "
        f"High above the quiet hills, a fluffy white cloud drifts down gracefully to greet your bedroom window. "
        f"This cloud is as warm as a soft fleece sweater, as pure as cotton, and as gentle as a mother's loving hug. "
        f"The friendly cloud invites little {name} to lie down upon its soft, cushioned back. "
        f"Feel how cozy and soothing it is as the cloud cradles your back, your arms, and your little tired feet. "
        f"The cloud floats gently through the night sky of the kingdom of {theme}... gliding peacefully above sleeping hills. "
        f"In the distance, sleepy cloud bunnies snuggle closely beside the smiling crescent moon. "
        f"The golden moon beams kindly upon {name} and whispers a soothing lullaby, "
        f"'Goodnight, precious child {name}... The evening sky watches over you with love and {lesson}.' "
        f"Friendly little stars form a warm golden canopy, filling your room with a soft, comforting glow. "
        f"Night blossoms open without a sound, releasing the calming scent of sweet chamomile and clover honey. "
        f"The cool mist wraps all around like a gentle blanket of peace and stillness. "
        f"There is no hurry here... The stars dim their bright lights so you can sleep peacefully through the night. "
        f"The sky swallows have tucked their wings atop the cloud peaks, fast asleep in the starry night. "
        f"A gentle mountain breeze softly strokes your forehead, brushing your hair with tender care. "
        f"Little silver wind chimes chime softly in the distance... ting... ting... singing a quiet lullaby. "
        f"Shhh... So quiet now... So warm, peaceful, and still... "
        f"Your eyelids feel heavier and heavier with each passing moment... "
        f"Your heart and breathing slow down to a steady, calm, peaceful rhythm. "
        f"Your fingers and toes are resting limp and cozy on the mattress. "
        f"The day has ended beautifully, and tomorrow brings fresh sunshine and joy. "
        f"You are deeply cherished, wonderfully safe, and loved forever. "
        f"Let your body drift away upon the cloud of sweet dreams... "
        f"Sleep tight, my sweet {name}... Goodnight... Rest in gentle peace..."
    )

def _toddler_kunang_en(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"The golden sun has slipped behind the western hills, leaving the green valley in peaceful twilight... "
        f"Little {name} lies comfortably in bed, ready to rest after a day full of fun and play. "
        f"Take a slow, gentle breath in... feeling the cool evening air flow into your chest... "
        f"and breathe out softly... letting all the day's tiredness melt away into the pillow... "
        f"Your warm blanket tucks around your toes and cuddles up to your relaxed shoulders. "
        f"Beside a calm, winding stream that flows without a single splash, thousands of friendly fireflies begin to glow. "
        f"Their golden lights flicker softly and rhythmically... glowing bright... then dimming gently... like the breath of the quiet night. "
        f"A tiny firefly carrying a miniature amber lantern rests on a bamboo leaf near where {name} is sleeping. "
        f"The little firefly speaks in a voice as soft as a quiet lute song echoing across the valley, "
        f"'Goodnight, little explorer {name}... This tranquil river valley surrounds you with warmth and {lesson}.' "
        f"The stream flows steadily on... its quiet murmur echoes like an endless, peaceful lullaby... "
        f"White water lilies on the pond have closed their petals for a long night's sleep under the moon. "
        f"Little golden fish rest quietly near the soft sandy riverbed in cool, clear water. "
        f"The tiny tree frogs whisper their sleepy evening song softer and softer... until all is still. "
        f"The wild ducks have tucked their bills beneath warm feathers on the quiet shore. "
        f"Night butterflies fold their delicate wings, resting safely under wide green lotus leaves. "
        f"Dewdrops glisten on the grass like tiny fallen stars asleep in the dark meadow. "
        f"The night breeze hums softly through the reeds, rocking the sleepy flowers to sleep. "
        f"Soft dew forms on the flower petals, glistening like little jewels in the moonlight. "
        f"Feel the quiet warmth of your blankets keeping you cozy and safe from head to toe. "
        f"The whole world seems to whisper together, 'Shhh... Time to sleep... Time to rest...' "
        f"Your eyelids are growing wonderfully heavy now... You feel so drowsy, so peaceful, and so secure... "
        f"Your body melts deeper into the cozy softness of your mattress and pillow. "
        f"Your breathing is calm... each breath slow, steady, and relaxed... "
        f"Every muscle in your little body lets go, resting completely without any weight. "
        f"You are safe here, watched over by the gentle lanterns of the night. "
        f"Close your eyes completely, little friend... Drift away into the sweetest sleep. "
        f"Goodnight, sweet {name}... Goodnight... Beautiful dreams await you..."
    )

def _toddler_kejora_en(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"The night sky stretches far and wide, like a deep indigo velvet blanket dusted with glowing jewels... "
        f"Little {name} is tucked safely beneath the warm covers, cozy and peaceful. "
        f"Take a deep, calming breath in... feeling the quiet harmony of the night fill your heart... "
        f"and exhale slowly... letting pure relaxation spread all the way to your fingertips and toes... "
        f"High in the eastern sky, the Morning Star shines with a bright, silvery, friendly glow. "
        f"A gentle beam of starlight reaches down like a shimmering silk ribbon to touch your window sill. "
        f"Upon this bridge of starlight, little {name} is invited to float weightlessly among fluffy silver clouds. "
        f"The Morning Star radiates a warm, soothing comfort that helps every little muscle feel loose and relaxed. "
        f"The smiling silver moon keeps watch beside you, radiating protection and affection. "
        f"The Morning Star whispers in a voice as gentle as a nighttime breeze, "
        f"'Goodnight, precious {name}... All the stars in the cosmos watch over your sleep in love and {lesson}.' "
        f"Little constellations dance slowly around you, turning in a soothing circle of quiet rest. "
        f"Friendly comets drift silently in the far distance, dusting the sky with shimmering gold stardust. "
        f"Soft lavender nebulae drift across the horizon, wrapping the heavens in bedtime warmth. "
        f"One by one, the shy little stars dim their glow to help you fall fast asleep. "
        f"The earth below is silent and still, resting peacefully in the dark night. "
        f"The forest trees are sleeping, and all the animal families are curled up together. "
        f"A soft celestial chime rings in the distance... ting... tong... so sweet, so gentle... "
        f"Golden starlight gently warms your face with a tender goodnight kiss. "
        f"Your blankets feel as soft as a cloud, wrapping you in peaceful warmth from head to toes. A gentle lullaby of starlight fills the room with comfort, reminding you how deeply you are loved. "
        f"Your eyelids feel heavier and heavier... Shhh... Feel the deep calm spreading through your thoughts... "
        f"Your breath is slow... steady... and so very comfortable... "
        f"Your pillow cradles your head with tenderness and unconditional love. "
        f"You are a very special child, deeply loved, and blessed with peace tonight. "
        f"Close your eyes tight, my darling... Let the light of the Morning Star carry you into deepest slumber. "
        f"Sleep well, sweet {name}... Goodnight... Rest peacefully in the arms of the universe..."
    )

# ==============================================================================
# 4. ENGLISH: OLDER KIDS (Age 4-8) Target: 660 - 750 words
# ==============================================================================

def _older_pinisi_en(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"The evening twilight in the western sky gradually fades into rich indigo velvet, scattered with a million silent stars. "
        f"{age}-year-old {name} lies comfortably beneath the warm blankets, feeling your heartbeat and breathing slow down into a steady, peaceful rhythm. "
        f"Take a long, deep breath in... letting clean, cool calm fill every corner of your mind... and exhale slowly, releasing all the day's energy into the night. "
        f"Let go of any hurry or busy thoughts from school and play, knowing that tonight your room is the safest, coziest place in the world. "
        f"Tonight, your imagination opens a secret gateway to a hidden tropical bay, where a majestic two-masted Pinisi ship named the Star Heritage rests upon water as clear as glass. "
        f"The tall canvas sails are woven from shimmering silver thread that catches the moonlight, billowing silently in the calm harbor air. "
        f"The teakwood decks and polished sandalwood timbers release a warm, comforting aroma of clove and sweet island spices. "
        f"As {name} steps onto the clean wooden deck, the Wise Captain greets you with an affectionate smile and serene eyes. "
        f"'Welcome aboard our night voyage, brave voyager {name},' the Captain murmurs in a voice as soothing as warm honey. "
        f"'Tonight we set sail across the Peaceful Sea toward the islands of {theme}, where the quiet wisdom of {lesson} will guide our dreams.' "
        f"The Pinisi glides forward effortlessly, parting the calm water into shimmering ripples that glow in the night. "
        f"Beneath the crystal-clear surface, thousands of golden bioluminescent jellyfish drift like underwater lanterns, lighting a tranquil path along the ocean floor. "
        f"A family of friendly dolphins surfaces gracefully beside the hull, swimming peacefully in rhythm without splashing a single drop onto the deck. "
        f"High above in the southern sky, the Southern Cross shines brilliantly, an eternal compass guiding all who travel with kindness and honesty. "
        f"The Captain gestures toward the bow. 'Remember, {name}, that even the mightiest ocean waves eventually settle into gentle, rhythmic ripples against the shore. "
        f"Whatever challenges you met today, tonight is your time to recharge completely, grounded in {lesson}.' "
        f"As the Captain speaks, a small bronze lantern glows warmly on the mainmast, casting a golden comfort into your heart. "
        f"Forward on the deck, a nocturnal traveler gently plucks a wooden lute, playing slow, hypnotic notes that blend into the murmur of the sea. "
        f"The night breeze softens to a gentle whisper... The silver sails are lowered silently by the night crew. "
        f"The Pinisi eases to a complete halt, floating peacefully in the middle of a sheltered, calm coral lagoon. "
        f"The dolphins slip quietly into the coral shadows, closing their eyes for the night in the warm reef waters. "
        f"The Captain guides {name} to a cozy cabin on deck, tucking you in with a handwoven silk quilt that is feather-light and pleasantly warm. "
        f"Listen to the quiet rhythm of the sea whispering against the hull... The gentle sway... rocking forward... rocking back... so soothing... so profoundly peaceful. "
        f"Feel a wave of relaxation rising from your toes, flowing through your calves, knees, and thighs, releasing every ounce of tension. "
        f"Your stomach and chest rise and fall in a tranquil, effortless rhythm... "
        f"Your back sinks comfortably into the mattress, your shoulders drop completely, and both arms rest limp and peaceful at your sides. "
        f"Your neck feels completely weightless, your jaw relaxes without any clenching, your forehead is cool and smooth, and your eyelids close softly in total comfort. "
        f"Your fingers uncurl and rest gently on top of the soft quilt as a quiet sigh escapes your lips. "
        f"Your eyelids are growing heavier with every passing second... Shhh... So heavy, so comfortable... "
        f"Your thoughts drift calmly, following the tranquil ocean currents toward deep, healing slumber. "
        f"Every breath in brings restorative calm; every breath out lets go of the world. "
        f"Your great adventures of today are complete, and tomorrow will bring fresh sunshine and exciting opportunities. "
        f"Sleep in peace and comfort, {name}... The stars over the quiet sea watch over you tonight. Goodnight... Sleep well... Sweet dreams..."
    )

def _older_kalpataru_en(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"A gentle night breeze rustles softly through ancient canopy leaves, carrying the fragrance of wild jasmine, orchid blossoms, and damp earth after a twilight shower. "
        f"{age}-year-old {name} pulls the warm blanket up to your chin, feeling the deep comfort and total security of your bed. "
        f"Take a long, slow breath in... feeling cool, clean serenity fill your chest... and exhale softly, allowing your shoulders to drop and completely relax. "
        f"Let every remaining thought from the day melt away into the quiet room, leaving only stillness and warmth. "
        f"At the border where waking life meets imagination lies the ancient Kalpataru Forest... a sacred, timeless sanctuary filled with gentle wonders and eternal peace. "
        f"Walking along a pathway of emerald moss as plush as a palace carpet, {name} encounters a magnificent giant tree whose bark shimmers with soft silver light. "
        f"This is the Kalpataru Tree of Life, where the forest gathers all the quiet peace of the universe. "
        f"The broad leaves murmur in the breeze like the strings of a classical harp playing a lullaby for the earth. "
        f"Massive roots anchor deeply into the soil, radiating a quiet stability that makes you feel completely safe. "
        f"Stepping softly from behind a grove of silver ferns comes Kancil, the wise mouse deer with a golden coat, accompanied by a gentle deer with luminous pearl antlers. "
        f"'Welcome, my friend {name},' Kancil whispers in a voice that is both noble and profoundly calming. "
        f"'We have long anticipated a young traveler who carries the sincere virtue of {lesson} and an open heart.' "
        f"The pearl-horned deer guides {name} to a crystal-clear spring at the base of the ancient roots, where pure water flows silently without a single hurried ripple. "
        f"High up on the protective branches, dozens of golden Birds of Paradise are already sleeping peacefully, their brilliant plumage tucked securely beneath their wings. "
        f"Kancil turns to {name} with an affectionate smile. 'True greatness in this life is never measured by how fast you run or how loud you shout, but by the quiet peace in your heart that radiates {lesson} to everyone around you.' "
        f"Those gentle words settle warmly into your mind, like a warm drink by the fireplace, soothing every corner of your spirit. "
        f"Kancil gives you a glowing golden acorn as a token of friendship, which you place safely in your pocket. "
        f"In the quiet distance, a soft bamboo xylophone played by forest guardians echoes gently through the moonlit trees... its notes slow, soothing, and mesmerizing. "
        f"All across the forest, the creatures have returned to their quiet nests for a long, restorative sleep. "
        f"Woodland rabbits cuddle deep in warm burrows; the wise night owl closes heavy eyes in the hollow of the oak tree. "
        f"Baby elephants rest leaning against their mothers in the silent meadow, breathing softly in peace. "
        f"The soft chirp of distant crickets and the rustle of leaves create a continuous, rhythmic lullaby that cradles the earth. "
        f"Listen to the wind moving through the treetops... Shhh... So still... So safe and calm... "
        f"Your eyelids feel delightfully heavy now... impossible to keep open against the sweet wave of sleepiness. "
        f"Feel a soothing wave of warmth gently gliding from the tips of your toes... "
        f"traveling smoothly up through your ankles, calves, knees, and thighs, dissolving every trace of muscle fatigue. "
        f"Your stomach and chest rise and fall in a tranquil, effortless rhythm... "
        f"Your back sinks comfortably into the mattress, your shoulders drop completely, and both arms rest limp and peaceful at your sides. "
        f"Your neck feels completely weightless, your jaw relaxes without any clenching, your forehead is cool and smooth, and your eyelids close softly in total comfort. "
        f"Your breathing is slow, steady, and quiet... The ancient Kalpataru forest surrounds you with eternal protection. "
        f"All the fatigue of today is gone, replaced by profound peace, deep gratitude, and quiet contentment. Your warm bed holds you safe and cradled in total serenity. "
        f"Sleep soundly, {name}... Tomorrow will bring a fresh chapter filled with laughter, wonder, and new discoveries. Goodnight..."
    )

def _older_awan_en(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"A delicate mist scented with night-blooming jasmine and wild mountain tea rolls gently across the silent emerald hills. "
        f"{age}-year-old {name} reclines into the warmth of the bed, feeling the quiet tranquility of the night settle all around you. "
        f"Take a deep, calming breath in... letting crisp, refreshing mountain air expand your lungs... and exhale slowly, feeling tension leave your body completely. "
        f"Let your thoughts quiet down like falling autumn leaves, welcoming the comforting stillness of your bedroom without any rush. "
        f"Before your inner eye, rolling tea plantations stretch beneath an expansive starlit canopy in the peaceful realm of {theme}. "
        f"In this serene valley, the evening breeze carries the distant, haunting melody of a bamboo flute, guiding your footsteps toward a magnificent stairway of silver clouds. "
        f"Each cloud step is firm yet pillowy soft, glowing with the gentle amber reflection of the moonlight. "
        f"At the summit of the cloud peaks stands the gentle Windkeeper, wearing flowing silk robes embroidered with morning stars. "
        f"He greets {name} with a respectful, welcoming bow and eyes filled with quiet joy. "
        f"'Welcome to the sanctuary of the Realm Above the Clouds, {name},' he speaks in a deep, resonant voice that soothes the mind. "
        f"'Tonight, the entire heavens give thanks for the quiet dedication, kindness, and {lesson} you have shown today.' "
        f"Looking down from this lofty cloud terrace, the whole world below rests peacefully in the dark embrace of the evening. "
        f"The distant city lights and village lanterns flicker faintly like drowsy fireflies preparing to sleep. "
        f"The Windkeeper hands {name} a warm ceramic mug of honeyed chamomile tea, warming your hands with soothing heat. "
        f"'Always remember,' he whispers with ancient wisdom, 'even the most fierce storm winds eventually quiet down before a heart anchored in patience and {lesson}.' "
        f"The mountain lakes below gleam like polished mirrors reflecting the spinning constellations. "
        f"Cloud pavilions surrounding you are lit by glowing crystal lanterns that gradually dim, matching the slow blinking of your heavy eyes. "
        f"Heavenly edelweiss blossoms open silently in the cool air, releasing a subtle perfume that relaxes every thought. "
        f"Wind chimes hanging from the eaves of the cloud pavilion sing a faint, delicate bedtime tune... ting... tong... soothing your spirit. All around the floating pavilion, celestial sky gardens bloom with petals tipped in silver starlight dew. The sweet scent of lavender, honeyed mountain tea, and jasmine blossoms drifts upon the cool mountain air, carrying a gentle wave of drowsiness into your mind. The Windkeeper smiles with deep kindness, noting how your eyelids flutter downward with each breath. The quiet valley far below is now completely asleep beneath a thick, peaceful blanket of silent white fog. A soft, comforting stillness rests gently over your bedroom, bringing absolute safety and peace. "
        f"The clouds draw gently closer together, forming a vast, welcoming bed softer than any feather mattress on earth. "
        f"The morning stars dim their brilliance one by one, creating a soothing twilight that invites deep slumber. "
        f"Listen to the quiet hum of the night sky... Shhh... Wonderfully still... So peaceful and calm... "
        f"Your eyelids are growing remarkably heavy... a delicious drowsiness flows through your veins. "
        f"Feel a soothing wave of warmth gently gliding from the tips of your toes... "
        f"traveling smoothly up through your ankles, calves, knees, and thighs, dissolving every trace of muscle fatigue. "
        f"Your stomach and chest rise and fall in a tranquil, effortless rhythm... "
        f"Your back sinks comfortably into the mattress, your shoulders drop completely, and both arms rest limp and peaceful at your sides. "
        f"Your neck feels completely weightless, your jaw relaxes without any clenching, your forehead is cool and smooth, and your eyelids close softly in total comfort. "
        f"Your breathing is deep, slow, and rhythmic... Your body feels weightless, floating upon clouds of peaceful sleep. "
        f"You are safe, you are protected, and you are deeply loved by the universe. "
        f"Let all your thoughts drift away into beautiful, restorative dreams. "
        f"Sleep deeply, {name}... The morning stars will watch over you until dawn. Goodnight... Sleep tight..."
    )

def _older_kunang_en(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"An ancient river valley gradually settles into the warm, quiet embrace of the night. "
        f"{age}-year-old {name} rests peacefully beneath the blankets, feeling your pulse and breathing slow down to a tranquil cadence. "
        f"Take a long, refreshing breath in... feeling clean night air fill your lungs... and exhale slowly, letting go of any stiffness or fatigue. "
        f"Allow any lingering worries or busy thoughts from the day to drift away on the evening breeze into the quiet dark. "
        f"In your imagination, the Valley of Glowing Fireflies unfolds... a hidden sanctuary where a crystal river flows smoothly between lush bamboo groves. "
        f"As the night reaches its deepest silence, millions of golden fireflies illuminate simultaneously along the riverbanks, casting a warm amber glow like thousands of fallen stars. "
        f"{name} walks across a sturdy floating wooden footbridge, greeted warmly by a magnificent Golden Stag standing calmly at the bamboo dock. "
        f"'Good evening, young traveler {name},' the Golden Stag greets you in a voice as warm as a hearthside fire. "
        f"'Tonight, this glowing valley offers its light in honor of the courage and {lesson} you hold within your heart.' "
        f"The Golden Stag invites you aboard a small raft crafted from fragrant sandalwood, which glides smoothly downstream with the gentle river current. "
        f"Upon the mirror-smooth surface of the water, the reflections of fireflies dance in slow, mesmerizing harmony with the current. "
        f"Ancient weeping willows drape their branches low over the water, filtering the night air into a soft whisper that lulls every traveler to sleep. "
        f"An old bamboo waterwheel at the river bend turns with a slow, hypnotic rhythm... creak... splash... water trickles peacefully... "
        f"The Golden Stag looks at the warm lantern at the bow of the raft and speaks softly, 'The greatest power in this world is never found in loudness, but in the quiet inner peace that shines with integrity and {lesson} in the dark.' "
        f"Those words bring a deep sense of relief to your mind, letting all the joints in your body feel loose, heavy, and comfortable. "
        f"The Golden Stag presents you with a small woven bamboo lantern glowing with a soothing ember, warming your hands. "
        f"A gentle flute player on an anchored fishing boat plays a soft lullaby, the notes floating lightly over the glassy water. Fragrant river reeds and sweet water lilies scent the cool night breeze, dissolving the very last remnants of tension from your thoughts. The Golden Stag nuzzles your hand with quiet affection, whispering that you are safe, cherished, and free to rest. "
        f"The raft docks quietly in a sheltered lotus cove, where pristine white water lilies have closed their petals in quiet slumber. "
        f"The fireflies begin to dim their lanterns by degrees, transitioning into a warm twilight that calls for deep sleep. "
        f"The wild river birds have tucked their heads under their wings on a quiet reed island. "
        f"The night wind murmurs through the bamboo stalks... a rhythmic, soothing whisper... Shhh... Rest now... Everything is safe and tranquil... "
        f"Your eyelids are too heavy to keep open any longer... The muscles in your neck, shoulders, and back release all their tightness. "
        f"Feel a soothing wave of warmth gently gliding from the tips of your toes... "
        f"traveling smoothly up through your ankles, calves, knees, and thighs, dissolving every trace of muscle fatigue. "
        f"Your stomach and chest rise and fall in a tranquil, effortless rhythm... "
        f"Your back sinks comfortably into the mattress, your shoulders drop completely, and both arms rest limp and peaceful at your sides. "
        f"Your neck feels completely weightless, your jaw relaxes without any clenching, your forehead is cool and smooth, and your eyelids close softly in total comfort. "
        f"The gentle murmur of the river carries away the last thoughts of waking hours into the calm night. "
        f"Your breath flows slowly, deeply, and regularly... Drift effortlessly along the river of eternal peace. "
        f"Tomorrow will arrive with a brilliant new sunrise and exciting adventures waiting for your footsteps. "
        f"Sleep soundly, {name}... The gentle lanterns of the valley will always illuminate your dreams. Goodnight..."
    )

def _older_kejora_en(name: str, age: int, theme: str, lesson: str) -> str:
    return (
        f"The infinite cosmos stretches boundlessly overhead, displaying spiral galaxies and shimmering stardust across a velvet canopy of night. "
        f"{age}-year-old {name} rests your head comfortably upon the pillow, feeling a wave of deep relaxation travel from the crown of your head to the tips of your toes. "
        f"Take a slow, expansive breath in... letting the quiet majesty of the universe expand within your mind... and release the breath slowly, letting your body sink deeper into the bed. "
        f"The long exhale carries away all the day's tasks, leaving only clear, tranquil stillness behind. "
        f"In your dreams tonight, a grand crystal observatory sits atop the peak of Mount Kejora, looking out directly into the breathtaking field of stars in {theme}. "
        f"At the center of the crystal dome, the Morning Star shines with magnificent grace, radiating a comforting spectrum of silver and sapphire light. "
        f"A wise Cosmic Voyager clothed in robes woven from starlight greets {name} with an affectionate, tranquil smile. "
        f"'Welcome to the celestial terrace, brave friend {name},' the voyager murmurs in a voice that resonates with quiet assurance. "
        f"'Tonight, the constellations have gathered to honor every act of goodwill and {lesson} you have shared in your world.' "
        f"The Cosmic Voyager invites {name} to sit upon a floating seat made from soft cosmic mist that cradles you in total comfort. "
        f"Through the crystal observatory arches, distant planets glide in slow, perfect orbits, moving in complete harmony without rushing. "
        f"The golden rings of Saturn turn gracefully like a cosmic phonograph playing the symphony of eternal silence. "
        f"A slender crescent moon floats near the window, casting a cool silver light that gently warms your cheek. "
        f"The Cosmic Voyager gazes warmly into your drowsy eyes and speaks gently, 'Even the brightest stars require the darkness of the night to reveal their true splendor. Your rest tonight is the foundation for your greatest strengths tomorrow, guided always by {lesson}.' "
        f"The warm cosmic glow seeps deep into your heart, dissolving every trace of doubt, fatigue, and worry. "
        f"Curtains of shimmering nebula dust glow softly around you, providing a profound sense of security. "
        f"A celestial crystal chime hums softly in the observatory hall... resonance echoing with gentle harmony... relaxing every cell in your body. Ancient star charts illuminated along the dome arches glow with reassuring amber light, mapping out centuries of quiet constellations that protect peaceful dreamers. The Cosmic Voyager drapes a starlight-woven quilt around your shoulders, light as a feather yet radiating comforting bedtime warmth. Outside, cosmic nebulae pulse like a slow, rhythmic lullaby, guiding your consciousness into complete surrender to rest. "
        f"The quiet celestial melody begins to fade into silence... The night comets glide peacefully beyond the horizon. "
        f"The lights within the observatory dome dim automatically, leaving only the gentle nightlight glow of the Morning Star. "
        f"Listen to the quiet heartbeat of the universe... Shhh... So profoundly still... Truly peaceful and calm... "
        f"Your eyelids feel overwhelmingly heavy... You feel wonderfully sleepy in the safety of the wide universe. "
        f"Feel a soothing wave of warmth gently gliding from the tips of your toes... "
        f"traveling smoothly up through your ankles, calves, knees, and thighs, dissolving every trace of muscle fatigue. "
        f"Your stomach and chest rise and fall in a tranquil, effortless rhythm... "
        f"Your back sinks comfortably into the mattress, your shoulders drop completely, and both arms rest limp and peaceful at your sides. "
        f"Your neck feels completely weightless, your jaw relaxes without any clenching, your forehead is cool and smooth, and your eyelids close softly in total comfort. "
        f"The gentle gravity of your warm bed holds you safe and cradled in total peace. "
        f"Your heart beats slowly and steadily... Your breathing is calm and deep, harmonized with the infinite night. "
        f"You are a treasured part of this universe, surrounded always by love and protection. "
        f"Close your eyes, star voyager... Let the sweet gravity of sleep carry you into the most beautiful dreams. "
        f"Sleep deeply, {name}... The Morning Star will watch over your rest until the morning light. Goodnight... Sleep well..."
    )


# ==============================================================================
# 5. EXPANDED FOLKLORE & NATURE ARCHETYPES (Borobudur, Toba, Bromo, Kereta Rimba)
# ==============================================================================

def _toddler_borobudur_id(name: str, age: int, theme: str, lesson: str) -> str:
    return f"Malam telah tiba di lembah hijau yang tenang di dekat Candi Borobudur yang agung... Semilir angin malam bertiup sepoi-sepoi, membelai pipi si kecil {name} yang bersiap tidur. Tarik napas perlahan... rasakan udara malam yang sejuk dan bersih masuk ke dada... lalu hembuskan dengan nyaman, perlahan, dan sangat lega... Tubuh mungilmu kini terasa begitu hangat, rileks, dan aman di atas peraduan yang empuk. Di kejauhan, stupa-stupa batu candi berdiri damai di bawah cahaya bulan purnama yang keemasan. Di teras candi yang hening, aroma bunga teratai putih semerbak berpadu dengan wanginya melati malam. Si kecil {name} berbaring nyaman di atas selimut sutra perak yang selembut awan kapas. Sebuah lonceng stupa batu kecil berdenting sangat lembut... ting... ting... bagai melodi tidur yang menenangkan sukma. Seekor burung merak malam yang anggun bertengger damai di dahan pohon beringin dekat pelataran candi. Burung merak itu melipat bulu-bulu ekornya yang indah dan memejamkan matanya dengan tenang sambil berbisik lembut, 'Selamat malam, anak manis {name}... Candi Borobudur yang damai ini selalu menjagamu dalam kehangatan dan {lesson}.' Relief-relief batu pada dinding candi memancarkan pendar keemasan yang menyejukkan pandangan mata. Kupu-kupu malam bersayap beludru hinggap perlahan di atas kelopak bunga melati, tertidur dalam keheningan. Ikan-ikan mas kecil di kolam air tenang beristirahat damai di bawah lindungan daun teratai yang lebar. Bunga-bunga teratai putih telah mengatupkan kelopaknya dengan anggun untuk tidur pulas semalaman. Kabut malam turun perlahan, menyelimuti bukit-bukit Menoreh di kejauhan dengan selimut tidur putih yang tebal. Lonceng angin bambu kecil berdenting sangat lembut di kejauhan... klinting... klinting... mengiringi setiap hembusan napas tidurmu yang teratur dan damai. Semua bintang di langit malam mengedipkan salam tidur yang hangat dan penuh kasih sayang. Kasurmu semakin empuk, selimutmu semakin nyaman melindungi tubuh mungilmu sepanjang malam. Kini suasana di sekelilingmu menjadi semakin hening... Shhh... Tenang sekali... Sungguh damai... Kelopak matamu mulai terasa semakin berat... begitu berat dan mengantuk... Napasmu menjadi semakin pelan, teratur, dan begitu ringan... seperti tetesan embun yang jatuh tanpa suara. Setiap hembusan napas melepaskan semua rasa lelah dari seharian bermain riang bersama keluarga. Punggungmu hangat... tangan dan kakimu terasa sangat santai dan lemas bersandar pada kasurmu yang empuk. Kamu adalah anak yang sangat baik, anak yang manis, dan senantiasa disayangi oleh seluruh keluargamu. Pejamkan matamu perlahan, sahabat cilik... Biarkan keheningan candi membawamu menuju pulau mimpi yang paling indah. Tidurlah yang nyenyak di pelukan malam yang hangat dan aman ini... Selamat tidur, sayangku {name}... Selamat malam... Mimpi indah... "

def _toddler_toba_id(name: str, age: int, theme: str, lesson: str) -> str:
    return f"Malam telah tiba di atas permukaan Danau Toba yang biru, tenang, dan luas membentang... Angin sejuk pegunungan bertiup lembut dari lereng Pulau Samosir, membelai pipi si kecil {name}. Tarik napas perlahan... rasakan kesegaran udara danau yang bersih memenuhi dadamu... lalu hembuskan perlahan-lahan... membiarkan seluruh tubuh mungilmu terasa rileks dan santai... Kasur tidurmu malam ini terasa begitu empuk dan hangat membungkus seluruh tubuhmu. Di tepi danau yang hening, air danau beriak sangat pelan dan berirama... kecipak... kecipuk... berbisik lembut membelai bebatuan halus. Pohon-pohon pinus di tepi tebing berdiri tegak bagai penjaga malam yang ramah, menebarkan wangi pinus yang menenangkan. Si kecil {name} berbaring nyaman di atas perahu kayu beratap ilalang yang hangat dan beralaskan bantal kapas tebal. Dari dalam danau yang jernih, seekor Ikan Mas Emas raksasa yang ramah muncul ke permukaan dengan gerakan sangat tenang. Sisik-sisik ikan itu memancarkan pendar keemasan lembut yang menghangatkan suasana malam di sekitar perahumu. Ikan Mas itu menatap si kecil {name} dengan penuh kasih sayang, lalu berbisik lembut dalam keheningan, 'Selamat malam, anak manis {name}... Danau Toba yang tenteram ini selalu menjagamu dengan limpahan cinta dan {lesson}.' Air danau memantulkan kilauan jutaan bintang dari langit malam yang tinggi dan jernih. Burung-burung bangau putih telah melipat lehernya yang ramping, tertidur lelap di sela rumpun gelagah tepian danau. Bebek-bebek danau telah berbaring nyaman di sarang rumput kering mereka di tepi pulau. Kabut sejuk turun dari puncak bukit, menyelimuti permukaan danau dengan selimut tidur putih yang damai. Lonceng angin bambu kecil berdenting sangat lembut di kejauhan... klinting... klinting... mengiringi setiap hembusan napas tidurmu yang teratur dan damai. Semua bintang di langit malam mengedipkan salam tidur yang hangat dan penuh kasih sayang. Kasurmu semakin empuk, selimutmu semakin nyaman melindungi tubuh mungilmu sepanjang malam. Kini suasana danau menjadi semakin hening... Shhh... Sangat tenang... Sungguh damai dan tenteram... Kelopak matamu mulai terasa semakin berat... begitu berat dan mengantuk... Napasmu menjadi semakin pelan, teratur, dan begitu ringan... bagai riak air danau yang tenang. Setiap hembusan napas melepaskan semua rasa lelah dari seharian bermain riang. Punggungmu hangat... tangan dan kakimu terasa sangat santai dan lemas bersandar pada kasurmu yang empuk. Kamu adalah anak yang sangat baik, anak yang manis, dan senantiasa disayangi oleh seluruh keluargamu. Pejamkan matamu perlahan, sahabat cilik... Biarkan ketenangan Danau Toba membawamu menuju pulau mimpi yang paling indah. Tidurlah yang nyenyak di pelukan malam yang hangat dan aman ini... Selamat tidur, sayangku {name}... Selamat malam... Mimpi indah... "

def _toddler_bromo_id(name: str, age: int, theme: str, lesson: str) -> str:
    return f"Malam telah tiba di padang sabana luas di kaki Gunung Bromo yang megah dan damai... Semilir angin pegunungan bertiup lembut melintasi lautan pasir berbisik, membelai pipi si kecil {name}. Tarik napas perlahan... rasakan udara malam yang sejuk, bersih, dan segar memenuhi dadamu... lalu hembuskan dengan nyaman, perlahan, dan sangat lega... Tubuh mungilmu kini terasa begitu hangat, rileks, dan aman di atas peraduan yang empuk. Di kejauhan, siluet perbukitan Teletubbies yang hijau terbentang anggun di bawah taburan jutaan bintang kejora. Di padang sabana yang sunyi, hamparan rumput ilalang bergoyang pelan seirama desau angin malam yang menenangkan. Si kecil {name} berbaring nyaman di atas kereta kayu beratap tenda kain wol yang tebal dan hangat. Seekor Kuda Bromo putih berbulu selembut sutra melangkah tenang mendekat ke samping peraduanmu. Kuda putih yang ramah itu menyandarkan kepalanya dengan lembut di dekat selimutmu, menghembuskan nafas hangat yang menyejukkan. Kuda Bromo berbisik dengan nada suara yang penuh kasih sayang, 'Selamat malam, anak manis {name}... Lembah sabana Bromo yang tenang ini selalu menjagamu dalam kehangatan dan {lesson}.' Pasir berbisik di lautan kaldera mengalunkan desau lirih bagai lagu tidur alam yang syahdu. Bunga-bunga edelweis abadi di lereng bukit mengatupkan kelopaknya, memancarkan wangi lembut yang menenangkan sukma. Burung-burung pipit sabana telah meringkuk damai di sarang rumput kering mereka di sela rumpun ilalang. Kabut malam turun perlahan dari kaldera, menyelimuti sabana hijau dengan selimut tidur putih yang sejuk dan damai. Lonceng angin bambu kecil berdenting sangat lembut di kejauhan... klinting... klinting... mengiringi setiap hembusan napas tidurmu yang teratur dan damai. Semua bintang di langit malam mengedipkan salam tidur yang hangat dan penuh kasih sayang. Kasurmu semakin empuk, selimutmu semakin nyaman melindungi tubuh mungilmu sepanjang malam. Kini suasana di sekelilingmu menjadi semakin hening... Shhh... Tenang sekali... Sungguh damai... Kelopak matamu mulai terasa semakin berat... begitu berat dan mengantuk... Napasmu menjadi semakin pelan, teratur, dan begitu ringan... seperti desau angin sabana yang lembut. Setiap hembusan napas melepaskan semua rasa lelah dari seharian bermain riang. Punggungmu hangat... tangan dan kakimu terasa sangat santai dan lemas bersandar pada kasurmu yang empuk. Kamu adalah anak yang sangat baik, anak yang manis, dan senantiasa disayangi oleh seluruh keluargamu. Pejamkan matamu perlahan, sahabat cilik... Biarkan keheningan Sabana Bromo membawamu menuju pulau mimpi yang paling indah. Tidurlah yang nyenyak di pelukan malam yang hangat dan aman ini... Selamat tidur, sayangku {name}... Selamat malam... Mimpi indah... "

def _toddler_kereta_id(name: str, age: int, theme: str, lesson: str) -> str:
    return f"Malam telah tiba di stasiun kayu tua di tepi hutan rimba tropis yang tenang dan damai... Semilir angin malam membawa aroma wangi bunga kopi dan tanah basah, membelai pipi si kecil {name}. Tarik napas perlahan... rasakan udara malam yang sejuk, bersih, dan harum memenuhi dadamu... lalu hembuskan dengan nyaman, perlahan, dan sangat lega... Tubuh mungilmu kini terasa begitu hangat, rileks, dan aman di atas peraduan yang empuk. Di atas rel besi yang kokoh, bersandar sebuah kereta uap kayu jati kecil yang sangat antik dan indah. Gerbong kereta ini beralaskan bantal-bantal beludru tebal dan selimut wol hangat berwarna biru tua bertabur bintang perak. Lampu minyak kereta memancarkan cahaya keemasan lembut yang menghangatkan suasana di dalam gerbong. Si kecil {name} melangkah masuk dan berbaring nyaman di dekat jendela kayu yang terbuka sedikit. Kereta uap mulai melaju perlahan... jes... gujes... jes... gujes... berirama lambat, tenang, dan teratur. Roda-roda besi berputar santai melintasi jembatan kayu jati di atas sungai hutan yang airnya mengalir pelan. Pak Masinis Kakek Beruang yang bijaksana menengok dari lokomotif sambil tersenyum ramah, lalu berbisik lembut, 'Selamat malam, penumpang cilik {name}... Kereta rimba yang tenteram ini selalu membawamu dalam keamanan dan {lesson}.' Di luar jendela, pohon-pohon jati dan pakis raksasa melambai pelan, ditemani kerlap-kerlip ribuan kunang- kunang hutan. Suara uap air dari cerobong lokomotif berbisik lirih... shhh... shhh... meninabobokan siapa pun yang mendengarnya. Kukang kecil berbulu halus tertidur pulas bergelantungan di dahan pohon randu dekat rel kereta. Burung hantu hutan memejamkan matanya dengan tenang di atas pucuk pohon pinus. Kabut malam turun perlahan, menyelimuti lintasan rel hutan dengan selimut tidur putih yang sejuk dan damai. Kini suara ayunan gerbong kereta menjadi semakin halus... Shhh... Tenang sekali... Sungguh damai... Kelopak matamu mulai terasa semakin berat... begitu berat dan mengantuk... Napasmu menjadi semakin pelan, teratur, dan begitu ringan... seirama laju kereta yang lembut. Setiap hembusan napas melepaskan semua rasa lelah dari seharian bermain riang. Punggungmu hangat... tangan dan kakimu terasa sangat santai dan lemas bersandar pada kasurmu yang empuk. Kamu adalah anak yang sangat baik, anak yang manis, dan senantiasa disayangi oleh seluruh keluargamu. Pejamkan matamu perlahan, sahabat cilik... Biarkan laju kereta rimba membawamu meluncur anggun menuju pulau mimpi yang paling indah. Tidurlah yang nyenyak di pelukan malam yang hangat dan aman ini... Selamat tidur, sayangku {name}... Selamat malam... Mimpi indah... Lonceng angin bambu kecil berdenting sangat lembut di kejauhan... klinting... klinting... mengiringi setiap hembusan napas tidurmu yang teratur dan damai. Semua bintang di langit malam mengedipkan salam tidur yang hangat dan penuh kasih sayang. Kasurmu semakin empuk, selimutmu semakin nyaman melindungi tubuh mungilmu sepanjang malam. "

def _older_borobudur_id(name: str, age: int, theme: str, lesson: str) -> str:
    return f"Kabut senja perlahan-lahan merayap turun menyelimuti lembah hijau Magelang, membungkus siluet megah Candi Borobudur dalam keheningan malam yang sakral. {name} yang berusia {age} tahun berbaring nyaman di bawah selimut hangat, merasakan detak jantung dan tarikan napas yang mulai melambat dengan sangat tenang. Tarik napas panjang dan dalam... rasakan ketenangan malam mengisi setiap sudut pikiranmu yang cerdas... lalu hembuskan perlahan-lahan ke udara bebas. Biarkan seluruh kepenatan setelah seharian belajar dan beraktivitas mengalir keluar dari tubuhmu bersama setiap hembusan napas yang damai. Malam ini, kamarmu adalah tempat yang paling aman, paling nyaman, dan paling tenang di seluruh dunia. Di alam imajinasimu, kamu melangkah di pelataran Candi Borobudur yang berlantai batu andesit sejuk di bawah naungan langit {theme} yang bertabur bintang kejora. Stupa-stupa berongga berdiri megah membentuk teras lingkaran keabadian, memancarkan aura kedamaian yang telah terjaga selama ribuan tahun. Dari dalam stupa utama, pendar cahaya keemasan lembut menyinari relief-relief batu kuno yang mengisahkan nilai-nilai luhur budi pekerti. Seorang Penjaga Dharma yang bijaksana dengan jubah putih bersahaja menyambut {name} dengan senyuman teduh penuh ketenteraman batin. 'Selamat malam, penjelajah berhati murni {name},' sapanya lirih dalam nada suara yang menenangkan kalbu. 'Malam ini, relief-relief abadi ini bersinar untuk merayakan ketulusan, kesabaran, dan {lesson} yang kamu tanamkan hari ini.' Penjaga Dharma mengajakmu duduk di atas teras stupa tertinggi, menghadap hamparan pepohonan pinus dan perbukitan Menoreh yang terlelap tidur. Lonceng batu berongga berdentang lirih ditiup semilir angin pegunungan... klenting... sebuah resonansi hening yang meredakan segala getaran cemas di dalam jiwa. Aroma dupa cendana dan bunga teratai malam menguap lembut di udara, membuai setiap indra tubuhmu dalam kenyamanan yang tiada tara. Penjaga Dharma berbisik penuh kebijaksanaan, 'Batu yang paling kokoh di candi ini tidak pernah tergesa-gesa menghadapi waktu. Begitu pula jiwamu... kedamaian sejati bermula saat kamu mampu melepaskan hari ini dengan penuh rasa syukur dan {lesson}.' Kata-kata bijak itu mengalir bagai air mata pegunungan yang jernih, menyejukkan rongga dadamu dan melepaskan semua ketegangan pikiran. Di sekeliling teras stupa, lentera-lentera batu minyak menyala temaram, menciptakan bayangan teduh yang bergetar lembut seirama desir angin malam. Hutan rimba purba di lereng Menoreh menghembuskan hawa sejuk yang menyegarkan setiap pori- pori kulitmu, membawa harum kayu cendana dan daun pakis basah. Dari kejauhan, aliran Sungai Progo dan Elo terdengar mengalir lirih bagai nyanyian tidur alam yang tak berujung, membilas sisa-sisa kepenatan pikiranmu. Burung-burung malam di ranting pohon kenanga tua merapatkan sayapnya, tertidur pulas dalam kehangatan sarang yang damai. Penjaga Dharma mengusap keningmu dengan jemari yang sejuk dan menenangkan, memberikan restu ketenteraman jiwa yang membimbingmu menuju tidur terdalam. Kini ribuan lampu minyak di pelataran candi meredup pelan satu demi satu, menyisakan pendar perak cahaya rembulan yang membelai lembut keningmu. Suara burung malam bersiul sangat lembut di dahan pohon bodhi kuno di kejauhan, menyanyikan kidung tidur abadi. Dengarkan detak keheningan semesta... Shhh... Sangat hening... Begitu damai dan tenteram... Di kejauhan, alunan seruling bambu malam terdengar mengalun syahdu terbawa angin pegunungan yang sejuk. Nada-nada damai itu meresap ke dalam relung batinmu, membilas segala sisa keletihan dan keraguan hari ini. Bintang-bintang di angkasa raya mengedipkan cahaya keemasan yang menaungi ruang tidurmu dengan rasa aman yang sejati. Setiap sel tubuhmu kini beristirahat penuh, menyerap energi ketenangan alam semesta yang tulus. Malam ini adalah waktu suci bagi jiwa dan ragamu untuk memulihkan kekuatan dan kedamaian batin. Selimut tebalmu terasa bagai dekapan hangat yang melindungi setiap impian indahmu. Kelopak matamu terasa sangat berat untuk dibuka kembali... Otot-otot leher, pundak, dan punggungmu melepas semua lelah. Rasakan gelombang kehangatan relaksasi merayap perlahan dari ujung jari-jari kakimu... merambat naik ke pergelangan kaki, betis, lutut, dan seluruh paha... melepaskan segala sisa ketegangan otot melangkah seharian ini. Perut dan dadamu kini bernapas dengan sangat ringan dan teratur... Punggungmu tenggelam nyaman ke dalam kasur, bahumu turun santai, dan kedua lenganmu beristirahat lemas di sisi tubuhmu. Lehermu terasa ringan, rahangmu melemas tanpa kertakan gigi, keningmu halus dan sejuk, dan kedua kelopak matamu menutup dengan sangat nyaman dan santai. Napasmu mengalir pelan, dalam, dan teratur... Hanyutlah dalam keheningan Candi Borobudur yang abadi. Hari esok akan datang dengan limpahan fajar baru yang gemilang dan peluang-peluang emas yang menunggu langkahmu. Tidurlah dengan nyenyak, {name}... Doa dan ketenteraman candi selalu menjagamu hingga fajar menyingsing. Selamat tidur dan selamat malam... "

def _older_toba_id(name: str, age: int, theme: str, lesson: str) -> str:
    return f"Matahari telah terbenam di balik dinding kaldera raksasa Danau Toba, meninggalkan pendar lembayung ungu yang perlahan-lahan meredup menjadi malam perak yang syahdu. {name} yang berusia {age} tahun berbaring santai di atas kasur yang empuk, merasakan detak jantung dan ritme napas yang melambat dengan sangat damai. Tarik napas panjang yang menenangkan... rasakan hawa malam pegunungan yang bersih memenuhi rongga dadamu... lalu hembuskan perlahan-lahan, melepaskan segala ketegangan hari ini. Biarkan kepenatan pikiranmu hanyut perlahan bersama hembusan napas yang panjang dan lega ke pelukan malam yang ramah. Di hadapan alam imajinasimu, terbentang luas perairan Danau Toba yang tenang bagai cermin raksasa di bawah naungan kubah langit {theme} yang bertabur rasi bintang. Di tengah perairan yang agung ini, Pulau Samosir berdiri megah dengan hamparan perbukitan hijau dan aroma segar hutan pinus yang menenangkan batin. Sebuah perahu kayu tradisional bertiang tunggal meluncur tanpa suara di atas permukaan air yang jernih, membelah pantulan cahaya rembulan perak. Dari kedalaman danau yang damai, sang Penjaga Danau yang berwujud Putri Ikan Mas Emas berenang anggun mengiringi perahumu dengan pendar cahaya hangat yang menyejukkan. 'Selamat malam, penjelajah muda yang budiman, {name},' sapa sang Penjaga dengan suara semerdu desau air terjun di kejauhan. 'Malam ini, danau kaldera yang sakral ini membentangkan ketenangannya untuk merayakan ketulusan, rasa syukur, dan {lesson} yang kamu miliki.' Sang Penjaga mengajakmu merapatkan perahu di sebuah teluk tersembunyi berpasir putih di lereng Samosir. Rumah adat beratap tanduk kerbau berdiri kokoh di tepian danau, dinaungi pohon beringin tua yang meneduhkan jiwa. Alunan musik kecapi Batak dan seruling hening mengalun pelan dari pondok kayu di kejauhan, membawakan nada-nada tidur yang membuai alam pikiranmu. Sang Penjaga Danau tersenyum lembut sambil berbisik penuh hikmah, 'Air danau ini begitu dalam karena ia mampu menampung segala hal dengan ketenangan tanpa gelisah. Begitu pula hatimu... kekayaan terbesarmu adalah kedamaian batin yang dipenuhi {lesson}.' Kata-kata bijak itu mengalir bagai tetesan embun pegunungan yang murni, menyejukkan seluruh rongga dada dan melepaskan semua beban pikiranmu. Air Danau Toba yang berwarna biru safir kini tenang tanpa riak, bagai kristal cair yang merefleksikan keindahan bintang- bintang di langit Nusantara. Di sepanjang lereng bukit pinus, kabut putih mengambang perlahan, menyaring udara malam menjadi begitu sejuk, bersih, dan harum getah pinus yang menenangkan. Air terjun Sipiso-piso di seberang tebing danau mengalirkan butiran kabut lembut yang melayang tertiup angin sepoi-sepoi, mendinginkan suasana peraduanmu. Perahu-perahu nelayan berlabuh tenang di dermaga kayu, berayun sangat lambat seirama detak napas tidur malam yang syahdu. Putri Ikan Mas mengepakkan sirip emasnya yang berkilau lembut di air telaga, menebarkan pendar kedamaian yang membuai seluruh tubuhmu dalam relaksasi sempurna. Kini lampu-lampu minyak di tepian teluk meredup pelan satu demi satu, menyisakan pendar bintang kejora yang bersinar teduh. Angin malam berbisik lirih melalui sela ranting pohon pinus... gemerisiknya terdengar bagai bisikan alam semesta... Shhh... Istirahatlah sekarang... Semuanya aman dan tenteram... Di kejauhan, alunan seruling bambu malam terdengar mengalun syahdu terbawa angin pegunungan yang sejuk. Nada-nada damai itu meresap ke dalam relung batinmu, membilas segala sisa keletihan dan keraguan hari ini. Bintang-bintang di angkasa raya mengedipkan cahaya keemasan yang menaungi ruang tidurmu dengan rasa aman yang sejati. Setiap sel tubuhmu kini beristirahat penuh, menyerap energi ketenangan alam semesta yang tulus. Malam ini adalah waktu suci bagi jiwa dan ragamu untuk memulihkan kekuatan dan kedamaian batin. Selimut tebalmu terasa bagai dekapan hangat yang melindungi setiap impian indahmu. Kelopak matamu terasa sangat berat untuk dibuka kembali... Otot-otot leher, pundak, dan punggungmu melepas semua lelah. Rasakan gelombang kehangatan relaksasi merayap perlahan dari ujung jari-jari kakimu... merambat naik ke pergelangan kaki, betis, lutut, dan seluruh paha... melepaskan segala sisa ketegangan otot melangkah seharian ini. Perut dan dadamu kini bernapas dengan sangat ringan dan teratur... Punggungmu tenggelam nyaman ke dalam kasur, bahumu turun santai, dan kedua lenganmu beristirahat lemas di sisi tubuhmu. Lehermu terasa ringan, rahangmu melemas tanpa kertakan gigi, keningmu halus dan sejuk, dan kedua kelopak matamu menutup dengan sangat nyaman dan santai. Irama detak jantungmu selaras dengan kedamaian Danau Toba yang abadi... Napasmu mengalir pelan, dalam, dan teratur... Hanyutlah dalam keheningan danau yang menyejukkan. Hari esok akan datang dengan limpahan fajar baru yang gemilang dan peluang-peluang emas yang menunggu langkahmu. Tidurlah dengan nyenyak, {name}... Ketenangan Danau Toba akan selalu menjaga mimpimu hingga mentari pagi tersenyum. Selamat malam... "

def _older_bromo_id(name: str, age: int, theme: str, lesson: str) -> str:
    return f"Matahari telah tenggelam di balik punggung Pegunungan Tengger, mengubah lautan pasir purba Bromo menjadi selimut malam yang dingin, megah, dan hening. {name} yang berusia {age} tahun berbaring nyaman di bawah selimut tebal yang hangat, merasakan detak jantung dan ritme napas yang melambat dengan sangat damai. Tarik napas panjang yang menenangkan... rasakan hawa malam pegunungan yang bersih memenuhi rongga dadamu... lalu hembuskan perlahan-lahan, melepaskan segala ketegangan hari ini. Biarkan kepenatan pikiranmu hanyut perlahan bersama hembusan napas yang panjang dan lega ke pelukan malam yang ramah. Di hadapan alam imajinasimu, terbentang luas hamparan Sabana Bromo dan Lautan Pasir Berbisik di bawah naungan kubah langit {theme} yang berkilau galaksi Bima Sakti. Puncak Bromo dan Batok berdiri kokoh dalam keheningan abadi, memancarkan aura keteguhan dan kedamaian alam yang tak tergoyahkan. Di padang sabana yang menghijau, rumput-rumput liar berdesau lembut ditiup angin sejuk, memainkan simfoni alam yang menenangkan jiwa. Seorang Penjaga Bromo yang bijaksana dengan kain sarung khas Tengger menyambutmu dengan senyuman hangat penuh kedamaian batin. 'Selamat malam, penjelajah muda yang tangguh, {name},' sapanya ramah dalam nada suara yang menyejukkan hati. 'Malam ini, lautan pasir berbisik ini menyanyikan kidung tidur untuk merayakan keberanian, ketulusan, dan {lesson} yang kamu ukir hari ini.' Sang Penjaga mengajakmu duduk di tepi perapian kayu pinus kecil yang memancarkan kehangatan lembut di bibir padang sabana. Di samping perapian, sekawanan kuda gunung Bromo berbulu tebal beristirahat tenang, menghembuskan nafas hangat yang bersahabat. Lonceng kayu di leher kuda berdenting perlahan ditiup angin... tong... tong... ritme sederhana yang meninabobokan pikiran yang lelah. Sang Penjaga Bromo menatap ke arah taburan bintang dan berbisik penuh hikmah, 'Lautan pasir ini mengajarkan kita bahwa dalam keheningan yang paling sepi sekalipun, semesta selalu menyediakan ketenangan bagi jiwa yang dipenuhi rasa syukur dan {lesson}.' Kata-kata bijak itu mengalir bagai air mata pegunungan yang jernih, menyejukkan rongga dadamu dan melepaskan semua ketegangan pikiran. Dari bibir kaldera, desau angin pasir terdengar mengalun ritmis bagai deru napas bumi yang sedang beristirahat pulas. Perbukitan Teletubbies di sekelilingmu tampak bagai ombak hijau raksasa yang tertidur tenang di bawah selimut kabut putih yang tebal. Bunga-bunga edelweis abadi yang tumbuh di lereng curam menebarkan keharuman segar pegunungan yang membersihkan sisa kepenatan pikiranmu. Api unggun kayu pinus perlahan mereda menjadi bara merah yang hangat, menyebarkan aroma damar yang membuai rasa kantukmu semakin dalam. Kuda-kuda sabana telah memejamkan mata mereka di atas hamparan rumput empuk, bernapas teratur dalam kenyamanan malam yang damai. Kini ribuan bintang di langit Bromo bersinar semakin terang namun teduh, menemani istirahatmu dengan kehangatan kosmis. Angin malam berbisik lirih melalui sela bukit pasir... desau lembutnya terdengar bagai senandung tidur semesta... Shhh... Istirahatlah sekarang... Semuanya aman dan tenteram... Di kejauhan, alunan seruling bambu malam terdengar mengalun syahdu terbawa angin pegunungan yang sejuk. Nada-nada damai itu meresap ke dalam relung batinmu, membilas segala sisa keletihan dan keraguan hari ini. Bintang-bintang di angkasa raya mengedipkan cahaya keemasan yang menaungi ruang tidurmu dengan rasa aman yang sejati. Setiap sel tubuhmu kini beristirahat penuh, menyerap energi ketenangan alam semesta yang tulus. Malam ini adalah waktu suci bagi jiwa dan ragamu untuk memulihkan kekuatan dan kedamaian batin. Selimut tebalmu terasa bagai dekapan hangat yang melindungi setiap impian indahmu. Kelopak matamu terasa sangat berat untuk dibuka kembali... Otot-otot leher, pundak, dan punggungmu melepas semua lelah. Rasakan gelombang kehangatan relaksasi merayap perlahan dari ujung jari-jari kakimu... merambat naik ke pergelangan kaki, betis, lutut, dan seluruh paha... melepaskan segala sisa ketegangan otot melangkah seharian ini. Perut dan dadamu kini bernapas dengan sangat ringan dan teratur... Punggungmu tenggelam nyaman ke dalam kasur, bahumu turun santai, dan kedua lenganmu beristirahat lemas di sisi tubuhmu. Lehermu terasa ringan, rahangmu melemas tanpa kertakan gigi, keningmu halus dan sejuk, dan kedua kelopak matamu menutup dengan sangat nyaman dan santai. Irama detak jantungmu selaras dengan desau pasir berbisik yang abadi... Napasmu mengalir pelan, dalam, dan teratur... Hanyutlah dalam keheningan Sabana Bromo yang menenteramkan. Hari esok akan datang dengan limpahan fajar baru yang gemilang dan peluang-peluang emas yang menunggu langkahmu. Tidurlah dengan nyenyak, {name}... Ketenangan Bromo akan selalu menjaga mimpimu hingga matahari terbit di ufuk timur. Selamat malam... "

def _older_kereta_id(name: str, age: int, theme: str, lesson: str) -> str:
    return f"Peluit uap kuno berbunyi sangat lirih dan lembut di stasiun peron kayu jati, membelah keheningan hutan rimba Nusantara yang mulai diselimuti kabut malam perak. {name} yang berusia {age} tahun berbaring nyaman di atas kasur gerbong yang empuk, merasakan detak jantung dan ritme napas yang melambat dengan sangat damai. Tarik napas panjang yang menenangkan... rasakan hawa malam hutan hujan tropis yang bersih memenuhi rongga dadamu... lalu hembuskan perlahan-lahan, melepaskan segala ketegangan hari ini. Biarkan kepenatan pikiranmu hanyut perlahan bersama hembusan napas yang panjang dan lega ke pelukan malam yang ramah. Di hadapan alam imajinasimu, terbentang jalur rel kereta uap antik yang membelah keheningan hutan tropis di bawah naungan kubah langit {theme} yang bertabur bintang kejora. Kereta Uap Rimba Nusantara ini terbuat dari kayu jati berukir indah, dengan jendela kaca kristal bundar dan lentera tembaga yang berpendar hangat. Roda-roda besi kereta mulai berputar dengan irama santai yang konstan... jes... gujes... jes... gujes... sebuah melodi mekanik yang menghanyutkan pikiran ke alam mimpi. Seorang Kondektur Rimba yang bijaksana berjas beludru cokelat menyapa {name} dengan anggukan teduh penuh kehangatan. 'Selamat malam, musafir muda yang berbudi luhur, {name},' sapanya ramah dalam nada suara yang menenangkan sukma. 'Malam ini, kereta ekspres hutan purba ini meluncur tenang untuk mengantarkanmu beristirahat, merayakan kerja keras, kesabaran, dan {lesson} yang kamu miliki.' Kondektur menyajikan secangkir cokelat jahe hangat yang mengepulkan uap beraroma kayu manis, menghangatkan kedua telapak tanganmu. Dari jendela gerbong yang nyaman, hutan rimba purba berlalu dalam gerakan yang lambat dan anggun. Pohon-pohon damar tua yang tinggi menjulang menyaring cahaya rembulan, menciptakan berkas-berkas perak di atas lantai gerbong. Di atas jembatan kayu yang melintasi ngarai sungai berarus tenang, pantulan lentera kereta tampak bergoyang lembut di permukaan air jernih. Kondektur tersenyum ramah dan berbisik penuh hikmah, 'Kereta yang baik tidak pernah terburu-buru mengejar stasiun akhir. Keindahan perjalanan terletak pada ketenangan langkah dan {lesson} di setiap stasiun hidupmu.' Kata-kata bijak itu mengalir bagai air mata pegunungan yang jernih, menyejukkan rongga dadamu dan melepaskan semua ketegangan pikiran. Uap lokomotif mengepul lembut ke udara malam, menyatu dengan kabut hutan dan aroma harum bunga melati hutan yang mekar di tepi rel. Gantungan lentera tembaga di langit-langit gerbong berayun lembut seirama goyangan rel yang santai, membiaskan pendar cahaya emas yang meneduhkan mata. Di balik rimbunnya pohon pakis raksasa, rusa-rusa hutan memandang kereta dengan tatapan bersahabat sebelum kembali meringkuk tidur lelap. Aliran sungai di bawah jembatan kayu menggemericik pelan bagai senandung penenang yang membersihkan setiap sisa kepenatan harimu. Kondektur Rimba meredupkan nyala lentera minyak di lorong gerbong, menciptakan suasana temaram yang sempurna untuk mengantar tidur. Kini laju kereta terasa semakin melambat, meluncur anggun di atas rel datar di tengah lembah bambu yang senyap. Suara desau uap lokomotif terdengar bagai bisikan penenang... shhh... shhh... Istirahatlah sekarang... Semuanya aman dan tenteram... Di kejauhan, alunan seruling bambu malam terdengar mengalun syahdu terbawa angin pegunungan yang sejuk. Nada-nada damai itu meresap ke dalam relung batinmu, membilas segala sisa keletihan dan keraguan hari ini. Bintang-bintang di angkasa raya mengedipkan cahaya keemasan yang menaungi ruang tidurmu dengan rasa aman yang sejati. Setiap sel tubuhmu kini beristirahat penuh, menyerap energi ketenangan alam semesta yang tulus. Malam ini adalah waktu suci bagi jiwa dan ragamu untuk memulihkan kekuatan dan kedamaian batin. Selimut tebalmu terasa bagai dekapan hangat yang melindungi setiap impian indahmu. Kelopak matamu terasa sangat berat untuk dibuka kembali... Otot-otot leher, pundak, dan punggungmu melepas semua lelah. Rasakan gelombang kehangatan relaksasi merayap perlahan dari ujung jari-jari kakimu... merambat naik ke pergelangan kaki, betis, lutut, dan seluruh paha... melepaskan segala sisa ketegangan otot melangkah seharian ini. Perut dan dadamu kini bernapas dengan sangat ringan dan teratur... Punggungmu tenggelam nyaman ke dalam kasur, bahumu turun santai, dan kedua lenganmu beristirahat lemas di sisi tubuhmu. Lehermu terasa ringan, rahangmu melemas tanpa kertakan gigi, keningmu halus dan sejuk, dan kedua kelopak matamu menutup dengan sangat nyaman dan santai. Irama detak jantungmu selaras dengan ritme ayunan kereta rimba yang menenangkan... Napasmu mengalir pelan, dalam, dan teratur... Hanyutlah dalam perjalanan mimpi yang abadi. Hari esok akan datang dengan limpahan fajar baru yang gemilang dan peluang- peluang emas yang menunggu langkahmu. Tidurlah dengan nyenyak, {name}... Kereta Rimba akan selalu menjagamu hingga stasiun fajar menyapa. Selamat malam... "

def _toddler_borobudur_en(name: str, age: int, theme: str, lesson: str) -> str:
    return f"Night has settled over the quiet emerald valley surrounding the magnificent Borobudur Temple... A gentle evening breeze rustles softly, brushing the cheek of little {name} as bedtime arrives. Take a slow, deep breath in... feeling the cool, clean night air fill your chest... and let it gently float out with a calm, comfortable sigh... Your little body feels so warm, so relaxed, and so safe tonight beneath the cozy covers. Across the mist, the stone bell stupas stand peacefully beneath the warm silver glow of the full moon. Upon the quiet temple terraces, the fragrance of white water lilies blends with sweet night jasmine. Little {name} rests comfortably upon a soft cloud-like blanket as gentle as morning fleece. A miniature stone bell stupa chimes with a tiny, delicate ring... ting... ting... singing a quiet lullaby for little ears. A graceful night peacock perches quietly on the ancient banyan branch near the temple courtyard. The peacock tucks its colorful feathers with gentle care and whispers softly, 'Goodnight, sweet {name}... The peaceful stone sanctuaries will keep you safe tonight in warmth and {lesson}.' Carved stone reliefs along the terraces glow with soothing amber starlight. Velvet night butterflies fold their delicate wings, resting upon fragrant blossom petals. Little golden fish in the temple reflection pool swim into their sleepy water lily beds. The white lotus blossoms floating on the calm temple ponds close their petals for deep sleep. Soft mountain fog wraps around the surrounding Menoreh hills like a bedtime blanket of pure quiet. A tiny silver wind chime sings softly in the distance... ting... ting... harmonizing with every gentle, steady breath you take beneath the warm blankets. All the stars in the night sky twinkle with warm, affectionate bedtime wishes. Your bed feels softer, and your covers wrap you in peaceful comfort for the entire night. Everything around you is becoming so peaceful... Shhh... Calm and still now... Your eyelids are growing heavier and heavier... so pleasantly sleepy... Your breathing is becoming slow, steady, and light, like a tiny raindrop falling on a soft green leaf. Every breath lets go of the day's play... Your arms and legs are completely relaxed on the mattress. You are safe, you are deeply loved by all your family, and you are wonderfully made. Close your eyes, little voyager... Let the tranquility of the ancient temple carry you toward the sweetest dreams. Sleep deeply and peacefully in this warm cocoon of rest... Goodnight, sweet {name}... Sleep tight... Sweet dreams... "

def _toddler_toba_en(name: str, age: int, theme: str, lesson: str) -> str:
    return f"Night has settled over the crystal blue waters of magnificent Lake Toba... A cool mountain breeze whispers down from the slopes of Samosir Island, softly brushing the cheek of little {name}. Take a slow, deep breath in... feeling the crisp, clean lake air fill your lungs... and let it gently drift away with a calm, relaxing sigh... Your bed feels so warm, so soft, and so comfortable tonight beneath the cozy covers. Along the quiet shore, the lake water ripples gently against smooth white pebbles... lap... lap... a rhythm as calm as a mother's lullaby. Tall pine trees on the green cliffs stand like friendly night guardians, sharing their soothing fragrance with the starry breeze. Little {name} rests peacefully inside a cozy wooden lake boat cushioned with fluffy pillows and warm woven blankets. From the clear, tranquil depths, a benevolent Golden Fish guardian rises quietly to the surface. Its golden scales reflect a soft, soothing amber warmth across the calm water around your boat. The gentle fish looks at sweet {name} with tender affection and whispers through the night air, 'Goodnight, precious child {name}... The tranquil waters of Lake Toba will hold you safe tonight in peace and {lesson}.' The lake surface turns into a silver mirror, reflecting the twinkling constellations of the clear night sky. White lake herons have tucked their slender beaks under soft wings, fast asleep among the tall reed grasses. Little lake ducks rest comfortably in their warm grass nests along the quiet shoreline. Cool night mist descends from the high volcanic crater, wrapping the lake in a blanket of peaceful white fog. A tiny silver wind chime sings softly in the distance... ting... ting... harmonizing with every gentle, steady breath you take beneath the warm blankets. All the stars in the night sky twinkle with warm, affectionate bedtime wishes. Your bed feels softer, and your covers wrap you in peaceful comfort for the entire night. Everything across the lake is becoming completely silent... Shhh... So very still... Restful and quiet now... Your eyelids are growing heavier and heavier... wonderfully sleepy... Your breathing is becoming slow, even, and gentle... like the calm, steady ripples of the deep lake. Every breath lets go of the day's excitement and play... Your arms and legs are completely relaxed. You are safe, you are deeply loved by all your family, and you are cherished beyond measure. Close your eyes, little explorer... Let the stillness of Lake Toba carry you into the sweetest, most restful dreams. Sleep deeply and safely in this quiet haven of rest... Goodnight, sweet {name}... Sleep tight... Sweet dreams... "

def _toddler_bromo_en(name: str, age: int, theme: str, lesson: str) -> str:
    return f"Night has settled over the vast green savanna at the foot of magnificent Mount Bromo... A crisp mountain breeze sweeps softly across the whispering sea of sand, gently brushing the cheek of little {name}. Take a slow, deep breath in... feeling the fresh, cool mountain air fill your chest... and let it gently float out with a calm, comfortable sigh... Your bed feels so warm, so relaxed, and so safe tonight beneath the soft, cozy blankets. Across the quiet distance, the gentle green rolling hills rest peacefully beneath millions of twinkling stars. In the quiet savanna, tall silver grasses sway softly in rhythm with the soothing mountain wind. Little {name} rests comfortably inside a sturdy wooden wagon lined with warm, woolly fleece blankets. A gentle white Bromo mountain pony with a silky mane walks softly to the side of your wagon. The friendly pony nuzzles near your blanket, breathing warm, comforting air into the cool night. The gentle pony whispers softly with tender affection, 'Goodnight, sweet {name}... The tranquil savanna of Bromo will hold you safe tonight in warmth and {lesson}.' The whispering sand across the caldera sings a gentle, soothing bedtime melody. Everlasting edelweiss blossoms along the hills close their petals, sharing a sweet mountain fragrance. Little savanna sparrows tuck their wings in their dry grass nests among the swaying reeds. Soft mountain mist floats down from the caldera, wrapping the green valley in a peaceful white bedtime blanket. A tiny silver wind chime sings softly in the distance... ting... ting... harmonizing with every gentle, steady breath you take beneath the warm blankets. All the stars in the night sky twinkle with warm, affectionate bedtime wishes. Your bed feels softer, and your covers wrap you in peaceful comfort for the entire night. Everything across the hills is becoming completely still... Shhh... Calm and peaceful now... Your eyelids are growing heavier and heavier... pleasantly sleepy... Your breathing is becoming slow, steady, and light, like the gentle whisper of the mountain wind. Every breath lets go of the day's play... Your arms and legs are completely relaxed on the mattress. You are safe, you are deeply loved by all your family, and you are wonderfully made. Close your eyes, little explorer... Let the tranquility of the Bromo savanna carry you toward the sweetest dreams. Sleep deeply and peacefully in this warm haven of quiet rest... Goodnight, sweet {name}... Sleep tight... Sweet dreams... "

def _toddler_kereta_en(name: str, age: int, theme: str, lesson: str) -> str:
    return f"Night has settled over the quaint wooden station at the edge of the quiet tropical rainforest... A cool night breeze carries the soothing scent of blooming coffee blossoms and damp earth, brushing the cheek of little {name}. Take a slow, deep breath in... feeling the crisp, fragrant forest air fill your chest... and let it gently float out with a calm, comfortable sigh... Your bed feels so warm, so relaxed, and so safe tonight beneath the soft, cozy blankets. Resting peacefully on the gleaming steel tracks stands a miniature antique teakwood steam train. The cozy train carriage is lined with thick velvet cushions and warm navy-blue blankets speckled with silver stars. A soft copper oil lamp glows with warm golden light, making the wooden cabin wonderfully inviting and peaceful. Little {name} steps inside and curls up comfortably beside the partially open wooden carriage window. The steam train begins to glide forward gently... chug... chug... chug... in a slow, steady, soothing rhythm. Its iron wheels roll effortlessly over wooden bridges crossing calm, murmuring forest streams. The wise old train conductor smiles warmly from the locomotive cabin and whispers tenderly, 'Goodnight, little passenger {name}... This tranquil rainforest train will carry you safely tonight in comfort and {lesson}.' Outside the window, giant ferns and ancient teak trees sway slowly, guided by thousands of glittering fireflies. The soft steam from the smokestack whispers through the leaves... shhh... shhh... singing a quiet lullaby. A sleepy little slow loris rests peacefully curled up in a high tree branch beside the tracks. A gentle forest owl closes its eyes in the quiet canopy, nestled securely in the stillness. Soft mountain fog settles over the tracks, wrapping the rainforest in a peaceful white bedtime blanket. The gentle rocking of the train carriage grows softer and softer... Shhh... Calm and peaceful now... Your eyelids are growing heavier and heavier... pleasantly sleepy... Your breathing is becoming slow, steady, and light, matching the gentle motion of the train. Every breath lets go of the day's play... Your arms and legs are completely relaxed on the mattress. You are safe, you are deeply loved by all your family, and you are wonderfully made. Close your eyes, little voyager... Let the quiet forest train carry you toward the sweetest dreams. Sleep deeply and peacefully in this warm haven of quiet rest... Goodnight, sweet {name}... Sleep tight... Sweet dreams... "

def _older_borobudur_en(name: str, age: int, theme: str, lesson: str) -> str:
    return f"Evening mist creeps quietly down over the verdant hills of Magelang, wrapping the majestic silhouette of Borobudur Temple in sacred nighttime stillness. {name}, who is {age} years old, rests comfortably under warm blankets, feeling the steady, calming cadence of heartbeat and breath. Take a slow, deep breath in... letting the tranquil night air fill every corridor of your bright mind... and release it gently into the open room. Let go of all the thoughts, lessons, and activities of the busy daytime, watching them dissolve into the peaceful evening breeze. Tonight, your bedroom is the safest, coziest, and most serene sanctuary in the entire world. In your quiet imagination, you step onto the smooth, cool volcanic stone terraces of Borobudur under a vast sky of {theme} studded with diamonds. Tier upon tier of stone stupas rise in circular harmony, radiating a profound serenity that has endured for centuries. Soft golden illumination emanates from within the central monument, casting gentle shadows across ancient carvings of wisdom and kindness. A serene Temple Guardian robed in simple white linen greets {name} with a peaceful, welcoming smile. 'Welcome, pure-hearted traveler {name},' the Guardian speaks in a soothing voice that immediately calms your spirit. 'Tonight, these timeless terraces glow in celebration of the patience, honesty, and {lesson} you have shown today.' The Guardian invites you to sit upon the highest terrace, gazing out over the sleepy emerald forests and sleeping Menoreh ridgeline. A distant hollow stone bell chimes softly in the cool mountain breeze... ting... a resonant, pure sound that cleanses all lingering worry from your thoughts. The scent of sandalwood and night-blooming lotus drifts through the cool mountain air, soothing every sense into tranquil comfort. The Guardian whispers, 'The greatest stones of this sanctuary never hurry through time. Your spirit too finds its true strength when you release the day in gratitude and {lesson}.' Those wise words settle deeply into your heart, relaxing the muscles around your temples and chest. Around the stone courtyards, soft earthen lamps flicker peacefully, casting gentle amber warmth across the ancient andesite blocks. The primeval rainforest along the valley whispers a quiet bedtime lullaby, carrying the fresh scent of wild mountain orchids and damp moss. Far below, the winding currents of the sacred Progo river murmur softly over smooth pebbles, washing away the final remnants of mental fatigue. Night birds nesting high in the bodhi branches tuck their heads beneath soft plumage, asleep in the embrace of the tranquil hills. The Guardian gently rests a hand of blessing near your shoulder, imparting a lasting sense of safety that cradles your sleep. Now the gentle oil lamps along the terrace dim one by one, leaving only the silver moonbeams kissing your forehead. A quiet night bird sings a soft, final melody from the ancient bodhi tree before resting its wings for the night. Listen to the quiet pulse of the universe... Shhh... Everything is tranquil... Peaceful and completely at rest... Far across the tranquil valley, the faint, soothing melody of a night flute drifts upon the cool mountain breeze. Those tranquil notes resonate within your heart, dissolving any remaining fatigue and restless thoughts from the busy day. The constellations above cast a warm, protective starlight across your bedroom, filling your space with genuine serenity. Every cell of your resting body absorbs the peaceful restorative energy of the quiet night. Tonight is a sacred time for your mind and spirit to restore their deepest strength and tranquility. Your soft blankets feel like a warm, loving cocoon sheltering every sweet dream that awaits you. Your eyelids feel pleasantly heavy... The muscles of your neck, shoulders, and back let go of all effort. Feel a soothing wave of warm relaxation washing over you from the tips of your toes... moving gently upward through your ankles, calves, knees, and thighs... releasing every trace of tension. Your chest and stomach rise and fall with an effortless, natural rhythm... Your back melts into the soft bed, your shoulders drop, and your arms rest completely limp at your sides. Your neck is weightless, your jaw relaxes, your forehead is cool and smooth, and your eyes remain softly closed in comfort. Your breath is slow, deep, and steady... Drift peacefully into the timeless sanctuary of Borobudur. Tomorrow will greet you with a brilliant sunrise and exciting new adventures waiting for your eager steps. Sleep deeply, {name}... The peace of the temple surrounds you until morning light. Goodnight and sweet dreams... "

def _older_toba_en(name: str, age: int, theme: str, lesson: str) -> str:
    return f"The golden sun has slipped behind the majestic volcanic caldera walls of Lake Toba, leaving behind a rich twilight indigo that gently deepens into starry stillness. {name}, who is {age} years old, rests comfortably under warm blankets, feeling the calm cadence of heartbeat and breath. Take a slow, deep breath in... letting the clean mountain pine air fill your lungs... and release it gently into the quiet night. Allow every remnant of daytime activity and study to dissolve with each relaxing exhale into the welcoming stillness of the evening. Tonight, your bedroom is your safe sanctuary of peace, warmth, and absolute comfort. In your quiet imagination, the vast mirror of Lake Toba stretches before you beneath an endless canopy of {theme} adorned with sparkling stars. In the heart of this ancient caldera, Samosir Island rises with emerald terraced hills, breathing the soothing aroma of mountain pine and wildflowers into the night. A slender wooden boat glides effortlessly across the glassy water, parting the shimmering silver reflections of the moon. From the tranquil depths, the benevolent Lake Guardian—a graceful Golden Fish shining with warm, luminous light—swims peacefully beside you. 'Welcome, thoughtful voyager {name},' speaks the Guardian with a voice as calming as a distant mountain waterfall. 'Tonight, these ancient waters spread their tranquility in honor of the kindness, patience, and {lesson} you have shown today.' The Guardian guides your boat toward a secluded white pebble bay nestled against the green slopes of Samosir. A traditional wooden house with soaring curved buffalo-horn eaves stands gracefully beside ancient banyan trees. Gentle notes of a wooden Batak flute and soft string lute float across the water, weaving a timeless melody of deep relaxation. The Guardian whispers, 'The lake is vast and deep because it holds all things in stillness without agitation. So too is your heart... your greatest strength lies in inner peace and {lesson}.' Those tranquil words flow like pure spring water into your spirit, relaxing the muscles across your shoulders, jaw, and chest. The sapphire waters of Lake Toba are completely still now, like liquid crystal holding the brilliant constellation reflections of the southern skies. Along the slopes of the pine forests, gentle mist curls slowly downward, filling the cool night air with sweet resin and wild mountain tea scents. Far across the caldera, the majestic Sipiso-piso waterfall murmurs like a perpetual bedtime whisper, rinsing away any lingering mental chatter. Fishermen's canoes rest securely tied to wooden moorings, rocking almost imperceptibly with the tranquil breathing of the sleeping lake. The Golden Fish swirls softly in the water, trailing a luminous ribbon of warm amber light that envelopes your senses in absolute calm. Now the distant shoreline lanterns fade into warm embers one by one, leaving only the steady glow of the morning star. The mountain breeze rustles softly through the pine needles... whispering gently to your sleepy senses... Shhh... Everything is peaceful... Deeply calm and safe... Far across the tranquil valley, the faint, soothing melody of a night flute drifts upon the cool mountain breeze. Those tranquil notes resonate within your heart, dissolving any remaining fatigue and restless thoughts from the busy day. The constellations above cast a warm, protective starlight across your bedroom, filling your space with genuine serenity. Every cell of your resting body absorbs the peaceful restorative energy of the quiet night. Tonight is a sacred time for your mind and spirit to restore their deepest strength and tranquility. Your soft blankets feel like a warm, loving cocoon sheltering every sweet dream that awaits you. Your eyelids feel wonderfully heavy... The muscles of your neck, shoulders, and back release all remaining tension. Feel a warm wave of relaxation moving gently upward from your toes... softening your ankles, calves, knees, and thighs into complete, effortless rest. Your chest and stomach rise and fall with an easy, natural rhythm... Your back sinks comfortably into the mattress, your shoulders drop, and your arms rest completely limp at your sides. Your neck is weightless, your jaw relaxes, your forehead is cool and smooth, and your eyes remain softly closed in comfort. Your breath is slow, deep, and steady... Drift peacefully into the timeless sanctuary of Lake Toba. Tomorrow will greet you with a brilliant sunrise and exciting new adventures waiting for your eager steps. Sleep deeply, {name}... The peace of the ancient lake watches over you until morning light. Goodnight and sweet dreams... "

def _older_bromo_en(name: str, age: int, theme: str, lesson: str) -> str:
    return f"The setting sun has slipped beneath the rugged crest of the Tengger caldera, transforming Bromo's primeval sea of sand into a cool, majestic sanctuary of nighttime peace. {name}, who is {age} years old, rests comfortably under thick, warm blankets, feeling the calm cadence of heartbeat and breath. Take a slow, deep breath in... letting the clean mountain air fill your lungs... and release it gently into the quiet night. Allow every remnant of daytime activity and study to dissolve with each relaxing exhale into the welcoming stillness of the evening. Tonight, your bedroom is your safe sanctuary of peace, warmth, and absolute comfort. In your quiet imagination, the vast emerald savanna and whispering sands of Bromo stretch beneath an endless canopy of {theme} blazing with the Milky Way. The sacred peaks of Bromo and Batok stand strong in timeless silence, radiating unwavering stability and natural calm. Across the grassy plains, wild mountain grasses whisper softly in the breeze, performing an ancient lullaby of nature. A wise Tengger Mountain Guardian wearing a warm woven patterned sash greets you with a calm, peaceful smile. 'Welcome, courageous traveler {name},' speaks the Guardian with a voice as comforting as a mountain lodge fire. 'Tonight, this whispering sand sea weaves its quiet melody to celebrate the bravery, honesty, and {lesson} you have shown today.' The Guardian invites you to rest beside a small pine-wood hearth casting gentle amber warmth across the edge of the savanna. Nearby, a herd of sturdy mountain horses rest quietly, their breath forming gentle clouds in the crisp starry air. A wooden bell around the lead horse chimes with a slow, soothing rhythm... clop... clop... easing all remaining mental fatigue. The Guardian looks up at the galaxy and whispers, 'The vast sand sea teaches us that in true quietness, the universe provides peace for every heart filled with gratitude and {lesson}.' Those tranquil words settle deeply into your thoughts, relaxing the muscles across your shoulders, jaw, and chest. Across the vast caldera, the rhythmic sigh of the whispering sands sounds like the calm breathing of the sleeping earth. The lush rolling savanna hills surrounding your camp look like giant green waves asleep beneath a thick blanket of silver starlight. Everlasting edelweiss blossoms clinging to the rugged crater cliffs release a fresh, invigorating scent that cleanses the mind. The campfire embers settle into a soft, steady crimson glow, wrapping the immediate air in cozy pine smoke warmth. The mountain horses close their dark, gentle eyes upon the soft meadow grass, breathing peacefully in nighttime harmony. Now the thousands of stars above Mount Bromo shine with a steady, tranquil glow that lights your journey into dreams. The mountain breeze rustles softly through the dry savanna grasses... Shhh... Everything is peaceful... Deeply calm and safe... Far across the tranquil valley, the faint, soothing melody of a night flute drifts upon the cool mountain breeze. Those tranquil notes resonate within your heart, dissolving any remaining fatigue and restless thoughts from the busy day. The constellations above cast a warm, protective starlight across your bedroom, filling your space with genuine serenity. Every cell of your resting body absorbs the peaceful restorative energy of the quiet night. Tonight is a sacred time for your mind and spirit to restore their deepest strength and tranquility. Your soft blankets feel like a warm, loving cocoon sheltering every sweet dream that awaits you. Your eyelids feel wonderfully heavy... The muscles of your neck, shoulders, and back release all remaining tension. Feel a warm wave of relaxation moving gently upward from your toes... softening your ankles, calves, knees, and thighs into complete, effortless rest. Your chest and stomach rise and fall with an easy, natural rhythm... Your back sinks comfortably into the mattress, your shoulders drop, and your arms rest completely limp at your sides. Your neck is weightless, your jaw relaxes, your forehead is cool and smooth, and your eyes remain softly closed in comfort. Your breath is slow, deep, and steady... Drift peacefully into the timeless sanctuary of the Bromo Savanna. Tomorrow will greet you with a brilliant sunrise and exciting new adventures waiting for your eager steps. Sleep deeply, {name}... The quiet strength of Bromo watches over you until morning light. Goodnight and sweet dreams... "

def _older_kereta_en(name: str, age: int, theme: str, lesson: str) -> str:
    return f"A gentle antique steam whistle sounds softly across the teakwood station platform, parting the quiet mist of the tropical rainforest at dusk. {name}, who is {age} years old, rests comfortably under thick, warm blankets, feeling the calm cadence of heartbeat and breath. Take a slow, deep breath in... letting the clean rainforest air fill your lungs... and release it gently into the quiet night. Allow every remnant of daytime activity and study to dissolve with each relaxing exhale into the welcoming stillness of the evening. Tonight, your bedroom is your safe sanctuary of peace, warmth, and absolute comfort. In your quiet imagination, the gleaming tracks of an antique steam train wind through the heart of the ancient forest beneath an endless canopy of {theme} blazing with stars. The Rainforest Express is crafted from rich polished teak, with circular brass lanterns casting warm amber light through quiet passenger compartments. The train wheels turn with an effortless, hypnotic rhythm... click-clack... click-clack... a mechanical melody carrying your thoughts toward peaceful rest. A wise Forest Conductor in a soft brown velvet coat greets you with a kind, reassuring smile. 'Welcome aboard the Rainforest Express, thoughtful traveler {name},' speaks the Conductor with a voice as calming as rain on teak leaves. 'Tonight, this peaceful journey celebrates the dedication, patience, and {lesson} you have shared today.' The Conductor serves a warm cup of spiced vanilla chamomile tea, warming your hands in deep comfort. Through the polished carriage window, the primeval forest drifts by in a graceful, dreamlike procession. Ancient dammar trees filter the silver moonlight into gentle beams that dance across the carpeted floor. Crossing a wooden trestle bridge high above a glass-smooth river, the lanterns cast shimmering amber ripples across the water. The Conductor whispers, 'A great train never rushes its passage through the night. The true beauty of any journey lies in peaceful steps and {lesson}.' Those tranquil words settle deeply into your thoughts, relaxing the muscles across your shoulders, jaw, and chest. Puffs of gentle steam rise quietly into the cool night air, blending with the scent of wild jasmine and damp cedar wood along the tracks. Hanging brass lamps swing gently with the hypnotic rocking of the train, creating a warm, drowsy amber twilight in your cabin. Deep in the giant fern groves, peaceful deer glance at the passing coaches with gentle eyes before returning to their quiet slumber. The stream below the wooden bridge murmurs a quiet bedtime lullaby, washing away the final remnants of mental fatigue. The Conductor turns down the oil lamps along the hallway, creating the perfect restful glow for deep sleep. Now the train glides effortlessly onto a smooth straightaway through a whispering bamboo grove. The gentle sigh of the locomotive steam whispers softly... shhh... shhh... Everything is peaceful... Deeply calm and safe... Far across the tranquil valley, the faint, soothing melody of a night flute drifts upon the cool mountain breeze. Those tranquil notes resonate within your heart, dissolving any remaining fatigue and restless thoughts from the busy day. The constellations above cast a warm, protective starlight across your bedroom, filling your space with genuine serenity. Every cell of your resting body absorbs the peaceful restorative energy of the quiet night. Tonight is a sacred time for your mind and spirit to restore their deepest strength and tranquility. Your soft blankets feel like a warm, loving cocoon sheltering every sweet dream that awaits you. Your eyelids feel wonderfully heavy... The muscles of your neck, shoulders, and back release all remaining tension. Feel a warm wave of relaxation moving gently upward from your toes... softening your ankles, calves, knees, and thighs into complete, effortless rest. Your chest and stomach rise and fall with an easy, natural rhythm... Your back sinks comfortably into the mattress, your shoulders drop, and your arms rest completely limp at your sides. Your neck is weightless, your jaw relaxes, your forehead is cool and smooth, and your eyes remain softly closed in comfort. Your breath is slow, deep, and steady... Drift peacefully into the timeless sanctuary of the Rainforest Express. Tomorrow will greet you with a brilliant sunrise and exciting new adventures waiting for your eager steps. Sleep deeply, {name}... The steady rhythm of the forest train watches over you until morning light. Goodnight and sweet dreams... "

TEMPLATES: Dict[Tuple[str, str, str], Any] = {
    # Indonesian Toddler (5 original + 4 expanded)
    ("id", "toddler", "perahu_pinisi"): _toddler_pinisi_id,
    ("id", "toddler", "hutan_kalpataru"): _toddler_kalpataru_id,
    ("id", "toddler", "negeri_atas_awan"): _toddler_awan_id,
    ("id", "toddler", "lentera_kunang_kunang"): _toddler_kunang_id,
    ("id", "toddler", "bintang_kejora"): _toddler_kejora_id,
    ("id", "toddler", "candi_borobudur"): _toddler_borobudur_id,
    ("id", "toddler", "danau_toba"): _toddler_toba_id,
    ("id", "toddler", "sabana_bromo"): _toddler_bromo_id,
    ("id", "toddler", "kereta_rimba"): _toddler_kereta_id,

    # Indonesian Older (5 original + 4 expanded)
    ("id", "older", "perahu_pinisi"): _older_pinisi_id,
    ("id", "older", "hutan_kalpataru"): _older_kalpataru_id,
    ("id", "older", "negeri_atas_awan"): _older_awan_id,
    ("id", "older", "lentera_kunang_kunang"): _older_kunang_id,
    ("id", "older", "bintang_kejora"): _older_kejora_id,
    ("id", "older", "candi_borobudur"): _older_borobudur_id,
    ("id", "older", "danau_toba"): _older_toba_id,
    ("id", "older", "sabana_bromo"): _older_bromo_id,
    ("id", "older", "kereta_rimba"): _older_kereta_id,

    # English Toddler (5 original + 4 expanded)
    ("en", "toddler", "perahu_pinisi"): _toddler_pinisi_en,
    ("en", "toddler", "hutan_kalpataru"): _toddler_kalpataru_en,
    ("en", "toddler", "negeri_atas_awan"): _toddler_awan_en,
    ("en", "toddler", "lentera_kunang_kunang"): _toddler_kunang_en,
    ("en", "toddler", "bintang_kejora"): _toddler_kejora_en,
    ("en", "toddler", "candi_borobudur"): _toddler_borobudur_en,
    ("en", "toddler", "danau_toba"): _toddler_toba_en,
    ("en", "toddler", "sabana_bromo"): _toddler_bromo_en,
    ("en", "toddler", "kereta_rimba"): _toddler_kereta_en,

    # English Older (5 original + 4 expanded)
    ("en", "older", "perahu_pinisi"): _older_pinisi_en,
    ("en", "older", "hutan_kalpataru"): _older_kalpataru_en,
    ("en", "older", "negeri_atas_awan"): _older_awan_en,
    ("en", "older", "lentera_kunang_kunang"): _older_kunang_en,
    ("en", "older", "bintang_kejora"): _older_kejora_en,
    ("en", "older", "candi_borobudur"): _older_borobudur_en,
    ("en", "older", "danau_toba"): _older_toba_en,
    ("en", "older", "sabana_bromo"): _older_bromo_en,
    ("en", "older", "kereta_rimba"): _older_kereta_en,
}

def get_story_fallback(archetype: str, age: int, is_id: bool, name: str, theme: str, lesson: str) -> str:
    lang = "id" if is_id else "en"
    tier = "toddler" if age <= 3 else "older"
    arch = archetype if (lang, tier, archetype) in TEMPLATES else "negeri_atas_awan"
    fn = TEMPLATES.get((lang, tier, arch), _toddler_awan_id)
    return fn(name=name, age=age, theme=theme, lesson=lesson)
