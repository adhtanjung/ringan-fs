<template>
  <div class="min-h-screen">
    <!-- Hero Section -->
    <section id="home" class="relative overflow-hidden bg-gradient-hero">
      <div class="container-custom section-padding">
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <div class="text-center lg:text-left animate-fade-in">
            <h1 class="text-4xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Merasa <span class="text-purple-600">lelah</span>? 
              <br><NuxtImg src="/image.png" alt="Ringan Logo" class="inline-block h-9 xl:h-14 md:h-10" /> hadir untuk <span class="text-blue-600">mendengarkan</span>.
            </h1>   
            <p class="text-xl text-gray-600 mb-8 max-w-2xl">
              AI-powered mental health support. <strong>Gratis, aman, dan anonim.</strong>
            </p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <NuxtLink to="/assessment">
                <Button size="lg" class="btn-primary text-white px-8 py-4 shadow-soft">
                  <Heart class="w-5 h-5 mr-2" />
                  Mulai Cek Kesehatan Mental
                </Button>
              </NuxtLink>
              <Button variant="outline" size="lg" class="border-purple-300 text-purple-700 hover:bg-purple-50 px-8 py-4 border-gradient">
                <Smartphone class="w-5 h-5 mr-2" />
                Download Aplikasi
              </Button>
            </div>
          </div>
          <div class="relative animate-float">
            <div class="bg-gradient-to-r from-purple-200 to-blue-200 rounded-3xl p-8 shadow-soft mt-8">
              <div class="bg-white rounded-2xl p-6 shadow-lg">
                <div class="flex items-center mb-4">
                  <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                    <Bot class="w-4 h-4 text-white" />
                  </div>
                  <span class="ml-3 font-semibold text-gray-700">Ringan AI</span>
                </div>
                <div class="space-y-3">
                  <div class="bg-purple-100 rounded-lg p-3 animate-fade-in">
                    <p class="text-sm text-gray-700">"Halo! Bagaimana perasaanmu hari ini?"</p>
                  </div>
                  <div class="bg-blue-100 rounded-lg p-3 ml-8 animate-fade-in" style="animation-delay: 0.2s">
                    <p class="text-sm text-gray-700">"Aku merasa sedikit cemas..."</p>
                  </div>
                  <div class="bg-purple-100 rounded-lg p-3 animate-fade-in" style="animation-delay: 0.4s">
                    <p class="text-sm text-gray-700">"Aku di sini untuk mendengarkan. Ceritakan lebih lanjut..."</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- What is Ringan Section -->
    <section id="about" class="section-padding bg-white">
      <div class="container-custom">
        <div class="text-center mb-16 animate-slide-up">
          <h2 class="text-3xl lg:text-5xl font-bold text-gray-900 mb-6">
            Apa itu <span class="gradient-text">Ringan</span>?
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Platform kesehatan mental yang dirancang khusus untuk generasi muda Indonesia
          </p>
        </div>
        
        <div class="grid md:grid-cols-3 gap-8 lg:gap-12">
          <Card class="text-center p-8 border-0 shadow-soft card-hover">
            <div class="w-16 h-16 bg-gradient-purple rounded-full flex items-center justify-center mx-auto mb-6 shadow-glow">
              <MessageCircleHeart class="w-8 h-8 text-white" />
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-4">AI Assistant yang Peduli</h3>
            <p class="text-gray-600">
              Ngobrol kapan saja dengan AI yang memahami perasaanmu, tanpa takut di-judge
            </p>
          </Card>
          
          <Card class="text-center p-8 border-0 shadow-soft card-hover">
            <div class="w-16 h-16 bg-gradient-blue rounded-full flex items-center justify-center mx-auto mb-6 shadow-glow">
              <Brain class="w-8 h-8 text-white" />
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-4">Self-Assessment Interaktif</h3>
            <p class="text-gray-600">
              Kenali dirimu lebih baik dengan tes psikologi yang mudah dipahami
            </p>
          </Card>
          
          <Card class="text-center p-8 border-0 shadow-soft card-hover">
            <div class="w-16 h-16 bg-gradient-green rounded-full flex items-center justify-center mx-auto mb-6 shadow-glow">
              <Users class="w-8 h-8 text-white" />
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-4">Komunitas Anonim & Artikel</h3>
            <p class="text-gray-600">
              Berbagi cerita dengan sesama dan akses artikel bermanfaat untuk kesehatan mental
            </p>
          </Card>
        </div>
        
        <div class="text-center mt-12">
          <NuxtLink to="/features" class="inline-block">
            <Button variant="outline" size="lg" class="border-purple-300 text-purple-700 hover:bg-purple-50 shadow-soft">
              Lihat Semua Fitur
            </Button>
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- Why Ringan Section -->
    <section id="why" class="section-padding bg-gradient-to-r from-purple-50 to-blue-50">
      <div class="container-custom">
        <div class="text-center mb-16">
          <h2 class="text-3xl lg:text-5xl font-bold text-gray-900 mb-6">
            Kenapa <span class="gradient-text">Ringan</span>?
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Kami memahami kekhawatiranmu dan menyediakan solusi yang tepat
          </p>
        </div>
        
        <div class="grid md:grid-cols-2 gap-8">
          <Card class="p-8 border-0 shadow-soft card-hover">
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                <ShieldAlert class="w-6 h-6 text-red-600" />
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900 mb-2">Takut di-judge</h3>
                <p class="text-gray-600 mb-4">Banyak yang ragu bercerita karena takut dinilai</p>
                <div class="flex items-center text-green-700">
                  <CheckCircle class="w-5 h-5 mr-2" />
                  <span class="font-semibold">Anonim sepenuhnya</span>
                </div>
              </div>
            </div>
          </Card>
          
          <Card class="p-8 border-0 shadow-soft card-hover">
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                <DollarSign class="w-6 h-6 text-red-600" />
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900 mb-2">Mahal?</h3>
                <p class="text-gray-600 mb-4">Terapi konvensional terlalu mahal untuk kantong mahasiswa</p>
                <div class="flex items-center text-green-700">
                  <CheckCircle class="w-5 h-5 mr-2" />
                  <span class="font-semibold">Mulai dari GRATIS</span>
                </div>
              </div>
            </div>
          </Card>
          
          <Card class="p-8 border-0 shadow-soft card-hover">
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                <FileText class="w-6 h-6 text-red-600" />
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900 mb-2">Ribet sign-up</h3>
                <p class="text-gray-600 mb-4">Formulir panjang dan proses pendaftaran yang menyulitkan</p>
                <div class="flex items-center text-green-700">
                  <CheckCircle class="w-5 h-5 mr-2" />
                  <span class="font-semibold">Login 1 klik, tanpa banyak tanya</span>
                </div>
              </div>
            </div>
          </Card>
          
          <Card class="p-8 border-0 shadow-soft card-hover">
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                <HelpCircle class="w-6 h-6 text-red-600" />
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900 mb-2">Bingung pilih psikolog</h3>
                <p class="text-gray-600 mb-4">Terlalu banyak pilihan, tidak tahu mana yang cocok</p>
                <div class="flex items-center text-green-700">
                  <CheckCircle class="w-5 h-5 mr-2" />
                  <span class="font-semibold">Direkomendasikan oleh AI & review nyata</span>
                </div>
              </div>
            </div>
          </Card>
        </div>
        
        <div class="text-center mt-12">
          <NuxtLink to="/assessment">
            <Button size="lg" class="btn-primary text-white px-8 py-4 shadow-soft">
              Mulai Gratis Sekarang
            </Button>
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section id="how" class="section-padding bg-white">
      <div class="container-custom">
        <div class="text-center mb-16">
          <h2 class="text-3xl lg:text-5xl font-bold text-gray-900 mb-6">
            Bagaimana <span class="gradient-text">Cara Kerjanya</span>?
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Proses sederhana dan privat untuk memulai perjalanan kesehatan mentalmu
          </p>
        </div>
        
        <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div class="text-center animate-fade-in">
            <div class="relative mb-6">
              <div class="w-20 h-20 bg-gradient-purple rounded-full flex items-center justify-center mx-auto shadow-glow">
                <Smile class="w-10 h-10 text-white" />
              </div>
              <div class="absolute -top-2 -right-2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-lg">
                <span class="text-sm font-bold text-purple-600">1</span>
              </div>
            </div>
            <h3 class="text-lg font-bold text-gray-900 mb-2">Check-in Mood Harian</h3>
            <p class="text-gray-600">Catat perasaanmu setiap hari dengan mudah</p>
          </div>
          
          <div class="text-center animate-fade-in" style="animation-delay: 0.2s">
            <div class="relative mb-6">
              <div class="w-20 h-20 bg-gradient-blue rounded-full flex items-center justify-center mx-auto shadow-glow">
                <ClipboardList class="w-10 h-10 text-white" />
              </div>
              <div class="absolute -top-2 -right-2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-lg">
                <span class="text-sm font-bold text-blue-600">2</span>
              </div>
            </div>
            <h3 class="text-lg font-bold text-gray-900 mb-2">Self-Assessment Singkat</h3>
            <p class="text-gray-600">Tes cepat untuk memahami kondisi mentalmu</p>
          </div>
          
          <div class="text-center animate-fade-in" style="animation-delay: 0.4s">
            <div class="relative mb-6">
              <div class="w-20 h-20 bg-gradient-green rounded-full flex items-center justify-center mx-auto shadow-glow">
                <MessageCircle class="w-10 h-10 text-white" />
              </div>
              <div class="absolute -top-2 -right-2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-lg">
                <span class="text-sm font-bold text-green-600">3</span>
              </div>
            </div>
            <h3 class="text-lg font-bold text-gray-900 mb-2">Ngobrol dengan Ringan AI</h3>
            <p class="text-gray-600">Curhat bebas dengan AI yang penuh empati</p>
          </div>
          
          <div class="text-center animate-fade-in" style="animation-delay: 0.6s">
            <div class="relative mb-6">
              <div class="w-20 h-20 bg-gradient-orange rounded-full flex items-center justify-center mx-auto shadow-glow">
                <ArrowRight class="w-10 h-10 text-white" />
              </div>
              <div class="absolute -top-2 -right-2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-lg">
                <span class="text-sm font-bold text-orange-600">4</span>
              </div>
            </div>
            <h3 class="text-lg font-bold text-gray-900 mb-2">Pilih Langkah Selanjutnya</h3>
            <p class="text-gray-600">Terapi profesional atau bergabung dengan komunitas</p>
          </div>
        </div>
        
        <div class="text-center mt-12">
          <NuxtLink to="/demo">
            <Button variant="outline" size="lg" class="border-green-300 text-green-700 hover:bg-green-50 shadow-soft">
              Lihat Demo Interaktif
            </Button>
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- Testimonials Section -->
    <section id="testimonials" class="section-padding bg-gradient-to-r from-blue-50 to-green-50">
      <div class="container-custom">
        <div class="text-center mb-16">
          <h2 class="text-3xl lg:text-5xl font-bold text-gray-900 mb-6">
            Suara <span class="gradient-text">Komunitas</span>
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Pengalaman nyata dari mereka yang telah merasakan manfaat Ringan
          </p>
        </div>
        
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <Card class="p-6 border-0 shadow-soft card-hover">
            <div class="flex items-center mb-4">
              <div class="w-12 h-12 bg-purple-200 rounded-full flex items-center justify-center">
                <User class="w-6 h-6 text-purple-600" />
              </div>
              <div class="ml-4">
                <p class="font-semibold text-gray-900">Mahasiswa, 22 tahun</p>
                <div class="flex text-yellow-400">
                  <Star class="w-4 h-4 fill-current" />
                  <Star class="w-4 h-4 fill-current" />
                  <Star class="w-4 h-4 fill-current" />
                  <Star class="w-4 h-4 fill-current" />
                  <Star class="w-4 h-4 fill-current" />
                </div>
              </div>
            </div>
            <p class="text-gray-600 italic">
              "Saya gak nyangka bisa merasa didengar walau cuma lewat AI. Ringan bener-bener bantu di masa sulit."
            </p>
          </Card>
          
          <Card class="p-6 border-0 shadow-soft card-hover">
            <div class="flex items-center mb-4">
              <div class="w-12 h-12 bg-blue-200 rounded-full flex items-center justify-center">
                <User class="w-6 h-6 text-blue-600" />
              </div>
              <div class="ml-4">
                <p class="font-semibold text-gray-900">Fresh Grad, 24 tahun</p>
                <div class="flex text-yellow-400">
                  <Star class="w-4 h-4 fill-current" />
                  <Star class="w-4 h-4 fill-current" />
                  <Star class="w-4 h-4 fill-current" />
                  <Star class="w-4 h-4 fill-current" />
                  <Star class="w-4 h-4 fill-current" />
                </div>
              </div>
            </div>
            <p class="text-gray-600 italic">
              "Fitur journaling dan artikel-artikelnya membantu banget waktu burnout kerja."
            </p>
          </Card>
          
          <Card class="p-6 border-0 shadow-soft card-hover md:col-span-2 lg:col-span-1">
            <div class="flex items-center mb-4">
              <div class="w-12 h-12 bg-green-200 rounded-full flex items-center justify-center">
                <User class="w-6 h-6 text-green-600" />
              </div>
              <div class="ml-4">
                <p class="font-semibold text-gray-900">Pekerja, 26 tahun</p>
                <div class="flex text-yellow-400">
                  <Star class="w-4 h-4 fill-current" />
                  <Star class="w-4 h-4 fill-current" />
                  <Star class="w-4 h-4 fill-current" />
                  <Star class="w-4 h-4 fill-current" />
                  <Star class="w-4 h-4 fill-current" />
                </div>
              </div>
            </div>
            <p class="text-gray-600 italic">
              "Akhirnya ada tempat yang aman untuk curhat tanpa takut di-judge. Recommended!"
            </p>
          </Card>
        </div>
      </div>
    </section>

    <!-- Retention Tools Section -->
    <section id="features" class="section-padding bg-white">
      <div class="container-custom">
        <div class="text-center mb-16">
          <h2 class="text-3xl lg:text-5xl font-bold text-gray-900 mb-6">
            Fitur yang Membuat <span class="gradient-text">Kamu Kembali</span>
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto">
            Tools yang membantu perjalanan kesehatan mentalmu jangka panjang
          </p>
        </div>
        
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <div class="space-y-8">
            <div class="flex items-start space-x-4 animate-fade-in">
              <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <TrendingUp class="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Dashboard Kemajuan Pribadi</h3>
                <p class="text-gray-600">Lihat perkembangan mood dan kesehatan mentalmu dari waktu ke waktu</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4 animate-fade-in" style="animation-delay: 0.2s">
              <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <Bell class="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Pengingat Personal & Program Terapi</h3>
                <p class="text-gray-600">Notifikasi yang membantu tanpa mengganggu, plus rencana terapi personal</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4 animate-fade-in" style="animation-delay: 0.4s">
              <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <Gift class="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Program Loyalitas</h3>
                <p class="text-gray-600">Dapatkan vouchers dan unlock fitur premium dengan konsistensi</p>
              </div>
            </div>
            
            <div class="flex items-start space-x-4 animate-fade-in" style="animation-delay: 0.6s">
              <div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <HeartHandshake class="w-6 h-6 text-orange-600" />
              </div>
              <div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Community Shoutouts</h3>
                <p class="text-gray-600">"Kamu gak sendiri" - Dukungan dari komunitas yang peduli</p>
              </div>
            </div>
          </div>
          
          <div class="relative animate-float">
            <div class="bg-gradient-to-br from-purple-100 to-blue-100 rounded-3xl p-8 shadow-soft">
              <div class="bg-white rounded-2xl p-6 shadow-lg mb-4">
                <div class="flex items-center justify-between mb-4">
                  <h4 class="font-bold text-gray-900">Dashboard Kemajuan</h4>
                  <MoreHorizontal class="w-5 h-5 text-gray-400" />
                </div>
                <div class="space-y-3">
                  <div class="flex items-center justify-between">
                    <span class="text-sm text-gray-600">Mood Tracking</span>
                    <span class="text-sm font-semibold text-green-600">↗ 15%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-green-500 h-2 rounded-full w-3/4"></div>
                  </div>
                </div>
              </div>
              
              <div class="bg-white rounded-2xl p-6 shadow-lg">
                <div class="flex items-center mb-3">
                  <Bell class="w-5 h-5 text-blue-600 mr-2" />
                  <span class="text-sm font-semibold text-gray-700">Reminder Hari Ini</span>
                </div>
                <p class="text-sm text-gray-600">"Jangan lupa check-in mood malam ini 💙"</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="section-padding bg-gradient-to-r from-purple-600 via-blue-600 to-green-600">
      <div class="container mx-auto px-4">
        <div class="max-w-4xl mx-auto text-center">
          <h2 class="text-3xl lg:text-5xl font-bold text-white mb-6">
            Kesehatan mentalmu penting.
          </h2>
          <p class="text-xl text-purple-100 mb-8 max-w-2xl mx-auto">
            Yuk mulai dari langkah kecil, bersama Ringan.
          </p>
          
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" class="bg-white text-purple-600 hover:bg-gray-100 px-8 py-4 shadow-soft">
              <Download class="w-5 h-5 mr-2" />
              Download Sekarang
            </Button>
            <NuxtLink to="/assessment">
              <Button size="lg" class="border-white text-white hover:bg-white hover:text-purple-600 px-8 py-4">
                <Heart class="w-5 h-5 mr-2" />
                Mulai Self-Assessment Gratis
              </Button>
            </NuxtLink>
          </div>
          
          <p class="text-purple-200 text-sm mt-6">
            Tersedia di Google Play Store • Gratis selamanya
          </p>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-16">
      <div class="container-custom">
        <div class="grid md:grid-cols-4 gap-8">
          <div class="md:col-span-2">
            <h3 class="text-2xl font-bold mb-4">Ringan</h3>
            <p class="text-gray-400 mb-6 max-w-md">
              Temukan ketenangan dalam genggaman. Ringan bantu kamu atasi stres, cemas, dan burnout — dengan cara yang aman, anonim, dan penuh empati.
            </p>
            <div class="flex space-x-4">
              <a href="#" class="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700 transition-colors">
                <Linkedin class="w-5 h-5" />
              </a>
              <a href="#" class="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700 transition-colors">
                <Instagram class="w-5 h-5" />
              </a>
              <a href="#" class="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700 transition-colors">
                <Music class="w-5 h-5" />
              </a>
            </div>
          </div>
          
          <div>
            <h4 class="text-lg font-semibold mb-4">Tentang</h4>
            <ul class="space-y-2 text-gray-400">
              <li><a href="#" class="hover:text-white transition-colors">Tentang Ringan</a></li>
              <li><NuxtLink to="/faq" class="hover:text-white transition-colors">FAQ</NuxtLink></li>
              <li><a href="#" class="hover:text-white transition-colors">Blog</a></li>
              <li><a href="#" class="hover:text-white transition-colors">Karir</a></li>
            </ul>
          </div>
          
          <div>
            <h4 class="text-lg font-semibold mb-4">Legal</h4>
            <ul class="space-y-2 text-gray-400">
              <li><NuxtLink to="/kebijakan-privasi" class="hover:text-white transition-colors">Kebijakan Privasi</NuxtLink></li>
              <li><NuxtLink to="/syarat-ketentuan" class="hover:text-white transition-colors">Syarat & Ketentuan</NuxtLink></li>
              <li><NuxtLink to="/hubungi-kami" class="hover:text-white transition-colors">Hubungi Kami</NuxtLink></li>
            </ul>
          </div>
        </div>
        
        <div class="border-t border-gray-800 mt-12 pt-8 text-center">
          <p class="text-gray-400">
            © 2024 Ringan. Semua hak cipta dilindungi. Dibuat dengan ❤️ untuk kesehatan mental Indonesia.
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { 
  Heart, 
  Smartphone, 
  Bot, 
  MessageCircleHeart, 
  Brain, 
  Users, 
  ShieldAlert, 
  CheckCircle, 
  DollarSign, 
  FileText, 
  HelpCircle, 
  Smile, 
  ClipboardList, 
  MessageCircle, 
  ArrowRight, 
  User, 
  Star, 
  TrendingUp, 
  Bell, 
  Gift, 
  HeartHandshake, 
  MoreHorizontal, 
  Download, 
  Linkedin, 
  Instagram, 
  Music 
} from 'lucide-vue-next'

// Meta tags for SEO
useSeoMeta({
  title: 'Ringan - AI Mental Health App untuk Generasi Muda Indonesia',
  ogTitle: 'Ringan - AI Mental Health App untuk Generasi Muda Indonesia',
  description: 'Temukan ketenangan dalam genggaman. Ringan bantu kamu atasi stres, cemas, dan burnout — dengan cara yang aman, anonim, dan penuh empati.',
  ogDescription: 'Temukan ketenangan dalam genggaman. Ringan bantu kamu atasi stres, cemas, dan burnout — dengan cara yang aman, anonim, dan penuh empati.',
  ogImage: '/og-image.jpg',
  twitterCard: 'summary_large_image',
})
</script>

<style scoped>
/* Custom smooth scrolling and animations */
.container {
  scroll-behavior: smooth;
}

/* Smooth hover animations */
.transition-shadow {
  transition: box-shadow 0.3s ease;
}

/* Custom gradient text */
.bg-gradient-to-br {
  background: linear-gradient(135deg, #f3e8ff 0%, #dbeafe 50%, #dcfce7 100%);
}
</style>
