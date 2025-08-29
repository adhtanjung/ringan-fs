<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-green-50">
    <!-- Header -->
    <div class="bg-white shadow-sm">
      <div class="container-custom py-8">
        <div class="text-center">
          <h1 class="text-4xl font-bold text-gray-900 mb-4">
            Frequently Asked Questions
          </h1>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto">
            Temukan jawaban atas pertanyaan yang sering ditanyakan tentang Ringan
          </p>
        </div>
      </div>
    </div>

    <!-- FAQ Content -->
    <div class="container-custom py-16">
      <div class="max-w-4xl mx-auto">
        <div class="space-y-6">
          <!-- FAQ Item 1 -->
          <div class="bg-white rounded-xl shadow-soft border border-gray-100">
            <button 
              @click="toggleFaq(0)"
              class="w-full text-left p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <h3 class="text-lg font-semibold text-gray-900">
                Apa itu Ringan dan bagaimana cara kerjanya?
              </h3>
              <ChevronDown 
                :class="{ 'rotate-180': openFaq === 0 }"
                class="w-5 h-5 text-gray-400 transition-transform"
              />
            </button>
            <div v-show="openFaq === 0" class="px-6 pb-6">
              <p class="text-gray-600 leading-relaxed">
                Ringan adalah aplikasi kesehatan mental berbasis AI yang dirancang khusus untuk generasi muda Indonesia. 
                Kami menyediakan layanan konseling AI 24/7, self-assessment untuk mengukur kesehatan mental, 
                dan platform untuk terhubung dengan psikolog profesional yang terverifikasi. Semua layanan tersedia 
                secara anonim dan gratis untuk memastikan privasi dan aksesibilitas.
              </p>
            </div>
          </div>

          <!-- FAQ Item 2 -->
          <div class="bg-white rounded-xl shadow-soft border border-gray-100">
            <button 
              @click="toggleFaq(1)"
              class="w-full text-left p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <h3 class="text-lg font-semibold text-gray-900">
                Apakah layanan Ringan benar-benar gratis?
              </h3>
              <ChevronDown 
                :class="{ 'rotate-180': openFaq === 1 }"
                class="w-5 h-5 text-gray-400 transition-transform"
              />
            </button>
            <div v-show="openFaq === 1" class="px-6 pb-6">
              <p class="text-gray-600 leading-relaxed">
                Ya, fitur-fitur utama Ringan tersedia gratis selamanya, termasuk AI chatbot, self-assessment, 
                dan akses ke artikel kesehatan mental. Kami juga menyediakan paket premium dengan fitur tambahan 
                seperti konsultasi video dengan psikolog, dashboard kemajuan yang lebih detail, dan program terapi personal. 
                Namun, kami berkomitmen untuk menjaga layanan dasar tetap gratis dan dapat diakses semua orang.
              </p>
            </div>
          </div>

          <!-- FAQ Item 3 -->
          <div class="bg-white rounded-xl shadow-soft border border-gray-100">
            <button 
              @click="toggleFaq(2)"
              class="w-full text-left p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <h3 class="text-lg font-semibold text-gray-900">
                Seberapa aman data pribadi saya di Ringan?
              </h3>
              <ChevronDown 
                :class="{ 'rotate-180': openFaq === 2 }"
                class="w-5 h-5 text-gray-400 transition-transform"
              />
            </button>
            <div v-show="openFaq === 2" class="px-6 pb-6">
              <p class="text-gray-600 leading-relaxed">
                Keamanan data adalah prioritas utama kami. Ringan menggunakan enkripsi AES untuk data yang tersimpan 
                dan HTTPS untuk semua komunikasi. Kami menerapkan prinsip anonimitas di mana pengguna dapat menggunakan 
                aplikasi tanpa harus memberikan identitas asli. Data sensitif disimpan di server yang berlokasi di Indonesia 
                dengan standar keamanan tinggi dan tidak akan dibagikan kepada pihak ketiga tanpa persetujuan eksplisit.
              </p>
            </div>
          </div>

          <!-- FAQ Item 4 -->
          <div class="bg-white rounded-xl shadow-soft border border-gray-100">
            <button 
              @click="toggleFaq(3)"
              class="w-full text-left p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <h3 class="text-lg font-semibold text-gray-900">
                Bagaimana cara kerja AI chatbot Ringan?
              </h3>
              <ChevronDown 
                :class="{ 'rotate-180': openFaq === 3 }"
                class="w-5 h-5 text-gray-400 transition-transform"
              />
            </button>
            <div v-show="openFaq === 3" class="px-6 pb-6">
              <p class="text-gray-600 leading-relaxed">
                AI chatbot Ringan dilatih menggunakan teknik pembelajaran mesin dengan dataset yang berfokus pada 
                kesehatan mental dan disesuaikan dengan konteks budaya Indonesia. Bot ini dapat memahami berbagai 
                masalah mental seperti stres, kecemasan, dan depresi, kemudian memberikan respons yang empatik 
                dan solusi praktis. Meskipun canggih, AI ini tidak menggantikan konsultasi dengan psikolog profesional 
                untuk kasus yang memerlukan penanganan khusus.
              </p>
            </div>
          </div>

          <!-- FAQ Item 5 -->
          <div class="bg-white rounded-xl shadow-soft border border-gray-100">
            <button 
              @click="toggleFaq(4)"
              class="w-full text-left p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <h3 class="text-lg font-semibold text-gray-900">
                Apakah hasil self-assessment dapat diandalkan?
              </h3>
              <ChevronDown 
                :class="{ 'rotate-180': openFaq === 4 }"
                class="w-5 h-5 text-gray-400 transition-transform"
              />
            </button>
            <div v-show="openFaq === 4" class="px-6 pb-6">
              <p class="text-gray-600 leading-relaxed">
                Self-assessment Ringan dikembangkan berdasarkan standar klinis yang telah tervalidasi seperti PHQ-9, 
                GAD-7, dan PSS-10. Hasil assessment memberikan gambaran awal tentang kondisi kesehatan mental Anda, 
                namun bukan sebagai diagnosis resmi. Hasil ini dapat membantu Anda memahami kondisi diri dan menentukan 
                langkah selanjutnya, termasuk apakah perlu berkonsultasi dengan psikolog profesional.
              </p>
            </div>
          </div>

          <!-- FAQ Item 6 -->
          <div class="bg-white rounded-xl shadow-soft border border-gray-100">
            <button 
              @click="toggleFaq(5)"
              class="w-full text-left p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <h3 class="text-lg font-semibold text-gray-900">
                Bagaimana cara menghubungkan dengan psikolog profesional?
              </h3>
              <ChevronDown 
                :class="{ 'rotate-180': openFaq === 5 }"
                class="w-5 h-5 text-gray-400 transition-transform"
              />
            </button>
            <div v-show="openFaq === 5" class="px-6 pb-6">
              <p class="text-gray-600 leading-relaxed">
                Setelah menyelesaikan self-assessment, sistem AI akan memberikan rekomendasi psikolog yang sesuai 
                dengan kebutuhan dan preferensi Anda. Anda dapat melihat profil lengkap psikolog, termasuk spesialisasi, 
                pengalaman, dan review dari klien sebelumnya. Proses booking dapat dilakukan langsung melalui aplikasi 
                dengan pilihan sesi online atau offline, tergantung ketersediaan psikolog.
              </p>
            </div>
          </div>

          <!-- FAQ Item 7 -->
          <div class="bg-white rounded-xl shadow-soft border border-gray-100">
            <button 
              @click="toggleFaq(6)"
              class="w-full text-left p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <h3 class="text-lg font-semibold text-gray-900">
                Apakah ada batasan usia untuk menggunakan Ringan?
              </h3>
              <ChevronDown 
                :class="{ 'rotate-180': openFaq === 6 }"
                class="w-5 h-5 text-gray-400 transition-transform"
              />
            </button>
            <div v-show="openFaq === 6" class="px-6 pb-6">
              <p class="text-gray-600 leading-relaxed">
                Ringan dirancang khusus untuk generasi muda Indonesia, dengan fokus utama pada rentang usia 16-35 tahun. 
                Untuk pengguna di bawah 18 tahun, kami menyarankan untuk melibatkan orang tua atau wali dalam proses 
                konsultasi dengan psikolog profesional. Konten dan pendekatan disesuaikan dengan tantangan mental health 
                yang spesifik dihadapi generasi muda, seperti academic pressure, quarter-life crisis, dan work-life balance.
              </p>
            </div>
          </div>

          <!-- FAQ Item 8 -->
          <div class="bg-white rounded-xl shadow-soft border border-gray-100">
            <button 
              @click="toggleFaq(7)"
              class="w-full text-left p-6 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <h3 class="text-lg font-semibold text-gray-900">
                Bagaimana jika saya mengalami krisis atau emergency?
              </h3>
              <ChevronDown 
                :class="{ 'rotate-180': openFaq === 7 }"
                class="w-5 h-5 text-gray-400 transition-transform"
              />
            </button>
            <div v-show="openFaq === 7" class="px-6 pb-6">
              <p class="text-gray-600 leading-relaxed">
                Ringan menyediakan fitur emergency button yang dapat diakses 24/7. Dalam situasi krisis, Anda akan 
                langsung terhubung dengan hotline darurat atau crisis counselor yang tersedia. Kami juga menyediakan 
                daftar kontak darurat seperti Hotline Bunuh Diri (119 ext 8), IGD Terdekat (112), dan Crisis Text Line. 
                Ingat, dalam situasi darurat, jangan ragu untuk segera menghubungi layanan darurat atau ke rumah sakit terdekat.
              </p>
            </div>
          </div>
        </div>

        <!-- Contact Section -->
        <div class="mt-16 text-center bg-white rounded-xl shadow-soft border border-gray-100 p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">
            Masih ada pertanyaan?
          </h2>
          <p class="text-gray-600 mb-6">
            Tim support kami siap membantu Anda
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <NuxtLink to="/hubungi-kami">
              <Button class="btn-primary text-white px-6 py-3">
                <MessageCircle class="w-5 h-5 mr-2" />
                Hubungi Kami
              </Button>
            </NuxtLink>
            <Button variant="outline" class="border-purple-300 text-purple-700 hover:bg-purple-50 px-6 py-3">
              <Mail class="w-5 h-5 mr-2" />
              Email Support
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ChevronDown, MessageCircle, Mail } from 'lucide-vue-next'

// Layout
definePageMeta({
  layout: 'default'
})

// Meta tags
useSeoMeta({
  title: 'FAQ - Ringan Mental Health App',
  description: 'Temukan jawaban atas pertanyaan yang sering ditanyakan tentang Ringan, aplikasi kesehatan mental AI untuk generasi muda Indonesia.',
})

// Reactive data
const openFaq = ref(null)

// Methods
const toggleFaq = (index) => {
  openFaq.value = openFaq.value === index ? null : index
}
</script>

<style scoped>
.container-custom {
  @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8;
}

.shadow-soft {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.btn-primary {
  @apply bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 transition-all duration-300;
}
</style> 