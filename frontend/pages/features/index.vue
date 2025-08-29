<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-green-50">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b">
      <div class="container-custom py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <NuxtLink to="/" class="flex items-center space-x-2">
              <div class="w-8 h-8 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center">
                <Heart class="w-4 h-4 text-white" />
              </div>
              <span class="text-xl font-bold text-gray-900">Ringan</span>
            </NuxtLink>
            <div class="hidden md:block w-px h-6 bg-gray-300"></div>
            <span class="hidden md:block text-sm text-gray-600">Semua Fitur</span>
          </div>
          <NuxtLink to="/" class="text-sm text-gray-600 hover:text-gray-900 flex items-center">
            <ArrowLeft class="w-4 h-4 mr-1" />
            Kembali ke Beranda
          </NuxtLink>
        </div>
      </div>
    </header>

    <div class="container-custom section-padding">
      <!-- Hero Section -->
      <div class="text-center mb-16">
        <h1 class="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
          Semua <span class="gradient-text">Fitur</span> Ringan
        </h1>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
          Temukan semua tools dan fitur yang membantu perjalanan kesehatan mentalmu
        </p>
        <div class="flex justify-center">
          <div class="bg-white rounded-full p-2 shadow-soft">
            <div class="flex space-x-1">
              <button
                v-for="(tab, index) in tabs"
                :key="tab.id"
                @click="activeTab = tab.id"
                :class="[
                  'px-4 py-2 rounded-full text-sm font-medium transition-all',
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                ]"
              >
                <component :is="tab.icon" class="w-4 h-4 mr-2 inline" />
                {{ tab.name }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="max-w-6xl mx-auto">
        <!-- Home Tab -->
        <div v-if="activeTab === 'home'" class="animate-fade-in">
          <div class="bg-white rounded-3xl p-8 lg:p-12 shadow-soft mb-8">
            <div class="flex items-center mb-8">
              <div class="w-16 h-16 bg-gradient-to-r from-purple-500 to-blue-500 rounded-2xl flex items-center justify-center mr-6">
                <Home class="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 class="text-3xl font-bold text-gray-900">Home Tab</h2>
                <p class="text-lg text-gray-600">Dashboard utama untuk aktivitas harian</p>
              </div>
            </div>
            
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center mb-4">
                  <Smile class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Daily Mood Check-In</h3>
                <p class="text-gray-600 mb-4">Emoji slider untuk melacak mood harian (😃🙂😐😞😭)</p>
                <div class="text-sm text-purple-700 font-medium">✓ Simpan ke riwayat mood</div>
              </div>

              <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center mb-4">
                  <Zap class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Quick Action Shortcuts</h3>
                <p class="text-gray-600 mb-4">Akses cepat ke fitur utama</p>
                <div class="space-y-1 text-sm text-blue-700 font-medium">
                  <div>• Self-assess</div>
                  <div>• Talk to AI</div>
                  <div>• Journal</div>
                </div>
              </div>

              <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center mb-4">
                  <TrendingUp class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Mood Trends Snapshot</h3>
                <p class="text-gray-600 mb-4">Grafik line chart dari 7 hari terakhir</p>
                <div class="text-sm text-green-700 font-medium">✓ Visualisasi perkembangan mood</div>
              </div>

              <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-orange-500 rounded-xl flex items-center justify-center mb-4">
                  <BookOpen class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Suggested Articles</h3>
                <p class="text-gray-600 mb-4">Artikel personal berdasarkan interaksi terakhir</p>
                <div class="text-sm text-orange-700 font-medium">✓ Rekomendasi AI</div>
              </div>

              <div class="bg-gradient-to-br from-pink-50 to-pink-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-pink-500 rounded-xl flex items-center justify-center mb-4">
                  <Bell class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Gentle Nudges</h3>
                <p class="text-gray-600 mb-4">Pengingat lembut untuk check-in harian</p>
                <div class="text-sm text-pink-700 font-medium">✓ "Kamu belum check-in hari ini"</div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Self-Assessment Tab -->
        <div v-if="activeTab === 'assessment'" class="animate-fade-in">
          <div class="bg-white rounded-3xl p-8 lg:p-12 shadow-soft mb-8">
            <div class="flex items-center mb-8">
              <div class="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-2xl flex items-center justify-center mr-6">
                <ClipboardList class="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 class="text-3xl font-bold text-gray-900">AI Self-Assessment</h2>
                <p class="text-lg text-gray-600">Evaluasi kesehatan mental dengan AI</p>
              </div>
            </div>
            
            <div class="grid md:grid-cols-2 gap-6">
              <div class="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center mb-4">
                  <MessageSquare class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Guided Assessment Flow</h3>
                <p class="text-gray-600 mb-4">21 pertanyaan dinamis untuk indikator stres dan kecemasan</p>
                <div class="text-sm text-blue-700 font-medium">✓ Pertanyaan adaptif berdasarkan jawaban</div>
              </div>

              <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center mb-4">
                  <Bot class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Conversational UX</h3>
                <p class="text-gray-600 mb-4">Interface chat dengan animasi menenangkan</p>
                <div class="text-sm text-purple-700 font-medium">✓ Pengalaman seperti ngobrol dengan teman</div>
              </div>

              <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center mb-4">
                  <BarChart3 class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Result Levels</h3>
                <p class="text-gray-600 mb-4">Output hasil: Ringan, Sedang, Berat</p>
                <div class="space-y-1 text-sm text-green-700 font-medium">
                  <div>• Deskripsi detail kondisi</div>
                  <div>• Saran tindak lanjut</div>
                </div>
              </div>

              <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-orange-500 rounded-xl flex items-center justify-center mb-4">
                  <Calendar class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">History Tracker</h3>
                <p class="text-gray-600 mb-4">Timeline assessment dan skor lengkap</p>
                <div class="text-sm text-orange-700 font-medium">✓ Pantau perkembangan dari waktu ke waktu</div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI Chatbot Tab -->
        <div v-if="activeTab === 'chatbot'" class="animate-fade-in">
          <div class="bg-white rounded-3xl p-8 lg:p-12 shadow-soft mb-8">
            <div class="flex items-center mb-8">
              <div class="w-16 h-16 bg-gradient-to-r from-green-500 to-teal-500 rounded-2xl flex items-center justify-center mr-6">
                <MessageCircle class="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 class="text-3xl font-bold text-gray-900">AI Chatbot</h2>
                <p class="text-lg text-gray-600">Teman AI yang siap mendengarkan kapan saja</p>
              </div>
            </div>
            
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div class="bg-gradient-to-br from-green-50 to-teal-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center mb-4">
                  <MessageSquare class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Chat Interface</h3>
                <p class="text-gray-600 mb-4">UI messaging real-time seperti WhatsApp</p>
                <div class="text-sm text-green-700 font-medium">✓ Typing indicator & timestamps</div>
              </div>

              <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center mb-4">
                  <Target class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Intent Modes</h3>
                <p class="text-gray-600 mb-4">Mode percakapan sesuai kebutuhan</p>
                <div class="space-y-1 text-sm text-blue-700 font-medium">
                  <div>• Ask for Help</div>
                  <div>• Daily Tips</div>
                  <div>• Free Talk</div>
                </div>
              </div>

              <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center mb-4">
                  <Brain class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Emotion Detection</h3>
                <p class="text-gray-600 mb-4">NLP untuk mengenali nada emosi</p>
                <div class="text-sm text-purple-700 font-medium">✓ Deteksi sedih, marah, cemas</div>
              </div>

              <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-orange-500 rounded-xl flex items-center justify-center mb-4">
                  <Lightbulb class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Smart Suggestions</h3>
                <p class="text-gray-600 mb-4">Balasan dinamis berdasarkan konteks</p>
                <div class="text-sm text-orange-700 font-medium">✓ "Mau bicara dengan psikolog?"</div>
              </div>

              <div class="bg-gradient-to-br from-red-50 to-red-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-red-500 rounded-xl flex items-center justify-center mb-4">
                  <Shield class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Crisis Protocol</h3>
                <p class="text-gray-600 mb-4">Trigger keyword untuk dukungan darurat</p>
                <div class="text-sm text-red-700 font-medium">✓ Koneksi langsung ke hotline</div>
              </div>

              <div class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-gray-500 rounded-xl flex items-center justify-center mb-4">
                  <Trash2 class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Privacy Control</h3>
                <p class="text-gray-600 mb-4">User bisa hapus seluruh chat history</p>
                <div class="text-sm text-gray-700 font-medium">✓ Kontrol penuh data pribadi</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Learn Tab -->
        <div v-if="activeTab === 'learn'" class="animate-fade-in">
          <div class="bg-white rounded-3xl p-8 lg:p-12 shadow-soft mb-8">
            <div class="flex items-center mb-8">
              <div class="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-2xl flex items-center justify-center mr-6">
                <BookOpen class="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 class="text-3xl font-bold text-gray-900">Learn Tab</h2>
                <p class="text-lg text-gray-600">Perpustakaan pengetahuan kesehatan mental</p>
              </div>
            </div>
            
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div class="bg-gradient-to-br from-orange-50 to-red-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-orange-500 rounded-xl flex items-center justify-center mb-4">
                  <FileText class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Curated Articles</h3>
                <p class="text-gray-600 mb-4">Tips kesehatan mental, cerita, konten berbasis sains</p>
                <div class="text-sm text-orange-700 font-medium">✓ Konten berkualitas tinggi</div>
              </div>

              <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center mb-4">
                  <Filter class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Tag Filters</h3>
                <p class="text-gray-600 mb-4">Filter berdasarkan topik spesifik</p>
                <div class="space-y-1 text-sm text-blue-700 font-medium">
                  <div>• Burnout • Focus • Sleep</div>
                  <div>• Stress • Relationships</div>
                </div>
              </div>

              <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center mb-4">
                  <Bookmark class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Save/Bookmark</h3>
                <p class="text-gray-600 mb-4">Simpan artikel untuk dibaca nanti</p>
                <div class="text-sm text-purple-700 font-medium">✓ Akses offline</div>
              </div>

              <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center mb-4">
                  <Sparkles class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">AI Recommendations</h3>
                <p class="text-gray-600 mb-4">Rekomendasi berdasarkan mood dan aktivitas</p>
                <div class="text-sm text-green-700 font-medium">✓ "Karena kamu merasa cemas kemarin..."</div>
              </div>

              <div class="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-indigo-500 rounded-xl flex items-center justify-center mb-4">
                  <Search class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Search Function</h3>
                <p class="text-gray-600 mb-4">Cari artikel berdasarkan keyword atau tag</p>
                <div class="text-sm text-indigo-700 font-medium">✓ Pencarian cerdas dengan filter</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Community Tab -->
        <div v-if="activeTab === 'community'" class="animate-fade-in">
          <div class="bg-white rounded-3xl p-8 lg:p-12 shadow-soft mb-8">
            <div class="flex items-center mb-8">
              <div class="w-16 h-16 bg-gradient-to-r from-pink-500 to-rose-500 rounded-2xl flex items-center justify-center mr-6">
                <Users class="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 class="text-3xl font-bold text-gray-900">Community Tab</h2>
                <p class="text-lg text-gray-600">Forum anonim untuk saling mendukung</p>
              </div>
            </div>
            
            <div class="grid md:grid-cols-2 gap-6">
              <div class="bg-gradient-to-br from-pink-50 to-rose-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-pink-500 rounded-xl flex items-center justify-center mb-4">
                  <MessageSquare class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Public Forums</h3>
                <p class="text-gray-600 mb-4">Forum tematik untuk berbagi pengalaman</p>
                <div class="space-y-1 text-sm text-pink-700 font-medium">
                  <div>• "Feeling Lonely"</div>
                  <div>• "Burnout Recovery"</div>
                  <div>• Dan tema lainnya</div>
                </div>
              </div>

              <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center mb-4">
                  <Edit3 class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Post & Reply</h3>
                <p class="text-gray-600 mb-4">Posting anonim dengan batasan kata</p>
                <div class="text-sm text-purple-700 font-medium">✓ Thread reply untuk diskusi mendalam</div>
              </div>

              <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-orange-500 rounded-xl flex items-center justify-center mb-4">
                  <Heart class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Reactions</h3>
                <p class="text-gray-600 mb-4">Tombol "Hug" dan sistem reaksi</p>
                <div class="text-sm text-orange-700 font-medium">✓ Cara sederhana menunjukkan dukungan</div>
              </div>

              <div class="bg-gradient-to-br from-red-50 to-red-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-red-500 rounded-xl flex items-center justify-center mb-4">
                  <Shield class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Moderation</h3>
                <p class="text-gray-600 mb-4">Sistem block/report dan filter keyword</p>
                <div class="text-sm text-red-700 font-medium">✓ Lingkungan yang aman dan positif</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Profile Tab -->
        <div v-if="activeTab === 'profile'" class="animate-fade-in">
          <div class="bg-white rounded-3xl p-8 lg:p-12 shadow-soft mb-8">
            <div class="flex items-center mb-8">
              <div class="w-16 h-16 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center mr-6">
                <User class="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 class="text-3xl font-bold text-gray-900">Profile Tab</h2>
                <p class="text-lg text-gray-600">Kelola akun dan preferensi personal</p>
              </div>
            </div>
            
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div class="bg-gradient-to-br from-indigo-50 to-purple-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-indigo-500 rounded-xl flex items-center justify-center mb-4">
                  <Edit class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Edit Profile</h3>
                <p class="text-gray-600 mb-4">Nama (opsional), emoji profil, preferensi</p>
                <div class="text-sm text-indigo-700 font-medium">✓ Personalisasi pengalaman</div>
              </div>

              <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center mb-4">
                  <BarChart3 class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Assessment History</h3>
                <p class="text-gray-600 mb-4">Timeline skor dan hasil sebelumnya</p>
                <div class="text-sm text-blue-700 font-medium">✓ Tracking progress jangka panjang</div>
              </div>

              <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center mb-4">
                  <Bookmark class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Bookmarked Articles</h3>
                <p class="text-gray-600 mb-4">Koleksi artikel yang disimpan</p>
                <div class="text-sm text-green-700 font-medium">✓ Perpustakaan personal</div>
              </div>

              <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center mb-4">
                  <Settings class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Notification Settings</h3>
                <p class="text-gray-600 mb-4">Toggle pengingat & prompt check-in</p>
                <div class="text-sm text-purple-700 font-medium">✓ Kontrol notifikasi sesuai kebutuhan</div>
              </div>

              <div class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-gray-500 rounded-xl flex items-center justify-center mb-4">
                  <Lock class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Privacy Options</h3>
                <p class="text-gray-600 mb-4">Hapus akun, clear chat data</p>
                <div class="text-sm text-gray-700 font-medium">✓ Kontrol penuh privasi</div>
              </div>

              <div class="bg-gradient-to-br from-orange-50 to-orange-100 rounded-2xl p-6">
                <div class="w-12 h-12 bg-orange-500 rounded-xl flex items-center justify-center mb-4">
                  <Info class="w-6 h-6 text-white" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-2">About Section</h3>
                <p class="text-gray-600 mb-4">Misi app, terms, kontak info</p>
                <div class="text-sm text-orange-700 font-medium">✓ Transparansi dan dukungan</div>
              </div>
            </div>
          </div>
        </div>

        <!-- System-Wide Features -->
        <div class="bg-gradient-to-r from-purple-600 via-blue-600 to-green-600 rounded-3xl p-8 lg:p-12 text-white">
          <h2 class="text-3xl font-bold mb-6 text-center">Fitur System-Wide</h2>
          <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div class="text-center">
              <div class="w-16 h-16 bg-white bg-opacity-20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Bell class="w-8 h-8 text-white" />
              </div>
              <h3 class="text-lg font-bold mb-2">Push Notifications</h3>
              <p class="text-purple-100 text-sm">Daily check-in, reading reminders</p>
            </div>
            
            <div class="text-center">
              <div class="w-16 h-16 bg-white bg-opacity-20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Wifi class="w-8 h-8 text-white" />
              </div>
              <h3 class="text-lg font-bold mb-2">Offline Mode</h3>
              <p class="text-purple-100 text-sm">Cached content dan chatbot replies</p>
            </div>
            
            <div class="text-center">
              <div class="w-16 h-16 bg-white bg-opacity-20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <UserCheck class="w-8 h-8 text-white" />
              </div>
              <h3 class="text-lg font-bold mb-2">Guest Mode</h3>
              <p class="text-purple-100 text-sm">Gunakan app tanpa akun</p>
            </div>
            
            <div class="text-center">
              <div class="w-16 h-16 bg-white bg-opacity-20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Shield class="w-8 h-8 text-white" />
              </div>
              <h3 class="text-lg font-bold mb-2">Data Encryption</h3>
              <p class="text-purple-100 text-sm">AES at rest, HTTPS in transit</p>
            </div>
          </div>
        </div>

        <!-- CTA Section -->
        <div class="text-center mt-16">
          <h2 class="text-3xl font-bold text-gray-900 mb-6">
            Siap mencoba semua fitur ini?
          </h2>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <NuxtLink to="/demo">
              <Button size="lg" class="btn-primary text-white px-8 py-4 shadow-soft">
                <Play class="w-5 h-5 mr-2" />
                Coba Demo Interaktif
              </Button>
            </NuxtLink>
            <Button variant="outline" size="lg" class="border-purple-300 text-purple-700 hover:bg-purple-50 px-8 py-4">
              <Download class="w-5 h-5 mr-2" />
              Download Aplikasi
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { 
  Heart,
  ArrowLeft,
  Home,
  ClipboardList,
  MessageCircle,
  BookOpen,
  Users,
  User,
  Smile,
  Zap,
  TrendingUp,
  Bell,
  Bot,
  MessageSquare,
  BarChart3,
  Calendar,
  Target,
  Brain,
  Lightbulb,
  Shield,
  Trash2,
  FileText,
  Filter,
  Bookmark,
  Sparkles,
  Search,
  Edit3,
  Edit,
  Settings,
  Lock,
  Info,
  Wifi,
  UserCheck,
  Play,
  Download
} from 'lucide-vue-next'

// Layout
definePageMeta({
  layout: false,
})

// Meta tags
useSeoMeta({
  title: 'Semua Fitur - Ringan AI Mental Health App',
  description: 'Jelajahi semua fitur lengkap Ringan: AI Chatbot, Self-Assessment, Community, Learn Tab, dan banyak lagi untuk kesehatan mentalmu.',
})

// Reactive data
const activeTab = ref('home')

const tabs = [
  { id: 'home', name: 'Home', icon: Home },
  { id: 'assessment', name: 'Assessment', icon: ClipboardList },
  { id: 'chatbot', name: 'AI Chat', icon: MessageCircle },
  { id: 'learn', name: 'Learn', icon: BookOpen },
  { id: 'community', name: 'Community', icon: Users },
  { id: 'profile', name: 'Profile', icon: User }
]
</script>

<style scoped>
.container-custom {
  @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8;
}

.section-padding {
  @apply py-12 lg:py-20;
}

.gradient-text {
  @apply bg-gradient-to-r from-purple-600 via-blue-600 to-green-600 bg-clip-text text-transparent;
}

.shadow-soft {
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.btn-primary {
  @apply bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 transition-all duration-300;
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 