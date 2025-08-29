<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-green-50">
    <!-- Header -->
    <div class="bg-white shadow-sm">
      <div class="container-custom py-8">
        <div class="text-center">
          <h1 class="text-4xl font-bold text-gray-900 mb-4">
            Kebijakan Privasi
          </h1>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto">
            Kami berkomitmen melindungi privasi dan keamanan data pribadi Anda
          </p>
          <p class="text-sm text-gray-500 mt-4">
            Terakhir diperbarui: {{ lastUpdated }}
          </p>
        </div>
      </div>
    </div>

    <!-- Privacy Policy Content -->
    <div class="container-custom py-16">
      <div class="max-w-4xl mx-auto">
        <!-- Introduction -->
        <div class="bg-white rounded-xl shadow-soft border border-gray-100 p-8 mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">Pendahuluan</h2>
          <p class="text-gray-600 leading-relaxed mb-4">
            Ringan ("kami", "aplikasi", atau "layanan") sangat menghargai privasi Anda. Kebijakan Privasi ini 
            menjelaskan bagaimana kami mengumpulkan, menggunakan, melindungi, dan membagikan informasi pribadi 
            Anda ketika menggunakan aplikasi kesehatan mental Ringan.
          </p>
          <p class="text-gray-600 leading-relaxed">
            Dengan menggunakan layanan kami, Anda menyetujui pengumpulan dan penggunaan informasi sesuai dengan 
            kebijakan ini. Kami berkomitmen untuk menjaga kepercayaan Anda dengan melindungi informasi pribadi 
            Anda sesuai dengan standar keamanan tertinggi.
          </p>
        </div>

        <!-- Information We Collect -->
        <div class="bg-white rounded-xl shadow-soft border border-gray-100 p-8 mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">Informasi yang Kami Kumpulkan</h2>
          
          <div class="space-y-6">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <Shield class="w-5 h-5 mr-2 text-purple-600" />
                Informasi yang Anda Berikan
              </h3>
              <ul class="text-gray-600 space-y-2 ml-7">
                <li>• Informasi akun (email, nama pengguna, kata sandi)</li>
                <li>• Informasi profil opsional (usia, jenis kelamin, lokasi umum)</li>
                <li>• Respons self-assessment dan survei kesehatan mental</li>
                <li>• Komunikasi dengan AI chatbot dan support team</li>
                <li>• Feedback, review, dan konten yang Anda buat</li>
              </ul>
            </div>

            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <Smartphone class="w-5 h-5 mr-2 text-blue-600" />
                Informasi yang Dikumpulkan Otomatis
              </h3>
              <ul class="text-gray-600 space-y-2 ml-7">
                <li>• Data penggunaan aplikasi (fitur yang digunakan, waktu penggunaan)</li>
                <li>• Informasi perangkat (model, sistem operasi, versi aplikasi)</li>
                <li>• Data log (crash reports, error logs untuk perbaikan aplikasi)</li>
                <li>• Data analitik penggunaan (untuk meningkatkan layanan)</li>
              </ul>
            </div>

            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <Heart class="w-5 h-5 mr-2 text-red-600" />
                Data Kesehatan Mental
              </h3>
              <p class="text-gray-600 leading-relaxed ml-7">
                Kami mengumpulkan dan memproses data kesehatan mental Anda (hasil assessment, mood tracking, 
                riwayat chat dengan AI) dengan enkripsi end-to-end dan perlindungan khusus sesuai regulasi 
                perlindungan data kesehatan.
              </p>
            </div>
          </div>
        </div>

        <!-- How We Use Information -->
        <div class="bg-white rounded-xl shadow-soft border border-gray-100 p-8 mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">Bagaimana Kami Menggunakan Informasi</h2>
          
          <div class="grid md:grid-cols-2 gap-6">
            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 flex items-center">
                <Target class="w-5 h-5 mr-2 text-green-600" />
                Tujuan Utama
              </h3>
              <ul class="text-gray-600 space-y-2">
                <li>• Menyediakan layanan kesehatan mental yang personal</li>
                <li>• Memberikan rekomendasi psikolog yang sesuai</li>
                <li>• Menganalisis kondisi mental dan memberikan insight</li>
                <li>• Menghubungkan dengan komunitas support yang relevan</li>
              </ul>
            </div>

            <div class="space-y-4">
              <h3 class="text-lg font-semibold text-gray-900 flex items-center">
                <Settings class="w-5 h-5 mr-2 text-purple-600" />
                Peningkatan Layanan
              </h3>
              <ul class="text-gray-600 space-y-2">
                <li>• Meningkatkan akurasi AI chatbot</li>
                <li>• Mengembangkan fitur-fitur baru</li>
                <li>• Memperbaiki bug dan performa aplikasi</li>
                <li>• Melakukan riset untuk kemajuan mental health tech</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Data Security -->
        <div class="bg-white rounded-xl shadow-soft border border-gray-100 p-8 mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">Keamanan Data</h2>
          
          <div class="grid md:grid-cols-3 gap-6">
            <div class="text-center p-4 bg-purple-50 rounded-lg">
              <Lock class="w-8 h-8 text-purple-600 mx-auto mb-3" />
              <h3 class="font-semibold text-gray-900 mb-2">Enkripsi AES-256</h3>
              <p class="text-sm text-gray-600">Data disimpan dengan enkripsi tingkat militer</p>
            </div>

            <div class="text-center p-4 bg-blue-50 rounded-lg">
              <Shield class="w-8 h-8 text-blue-600 mx-auto mb-3" />
              <h3 class="font-semibold text-gray-900 mb-2">HTTPS/TLS</h3>
              <p class="text-sm text-gray-600">Semua komunikasi data terenkripsi</p>
            </div>

            <div class="text-center p-4 bg-green-50 rounded-lg">
              <Server class="w-8 h-8 text-green-600 mx-auto mb-3" />
              <h3 class="font-semibold text-gray-900 mb-2">Server Indonesia</h3>
              <p class="text-sm text-gray-600">Data disimpan di server aman Indonesia</p>
            </div>
          </div>

          <div class="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div class="flex items-start">
              <AlertTriangle class="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
              <div>
                <h3 class="font-semibold text-yellow-800 mb-1">Komitmen Keamanan</h3>
                <p class="text-sm text-yellow-700">
                  Kami melakukan audit keamanan rutin, penetration testing, dan mengikuti best practices 
                  industry untuk melindungi data sensitif kesehatan mental Anda.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Data Sharing -->
        <div class="bg-white rounded-xl shadow-soft border border-gray-100 p-8 mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">Pembagian Data dengan Pihak Ketiga</h2>
          
          <div class="space-y-6">
            <div class="flex items-start space-x-4">
              <CheckCircle class="w-6 h-6 text-green-500 mt-1 flex-shrink-0" />
              <div>
                <h3 class="font-semibold text-gray-900 mb-2">Psikolog Partner</h3>
                <p class="text-gray-600">
                  Data relevan dibagikan hanya kepada psikolog yang Anda pilih untuk konsultasi, 
                  dengan persetujuan eksplisit Anda.
                </p>
              </div>
            </div>

            <div class="flex items-start space-x-4">
              <CheckCircle class="w-6 h-6 text-green-500 mt-1 flex-shrink-0" />
              <div>
                <h3 class="font-semibold text-gray-900 mb-2">Service Providers</h3>
                <p class="text-gray-600">
                  Penyedia layanan cloud, analytics, dan payment gateway dengan kontrak perlindungan data ketat.
                </p>
              </div>
            </div>

            <div class="flex items-start space-x-4">
              <X class="w-6 h-6 text-red-500 mt-1 flex-shrink-0" />
              <div>
                <h3 class="font-semibold text-gray-900 mb-2">Yang TIDAK Kami Lakukan</h3>
                <p class="text-gray-600">
                  Kami TIDAK PERNAH menjual, menyewakan, atau membagikan data pribadi Anda untuk 
                  tujuan komersial atau marketing pihak ketiga.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Your Rights -->
        <div class="bg-white rounded-xl shadow-soft border border-gray-100 p-8 mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">Hak-Hak Anda</h2>
          
          <div class="grid md:grid-cols-2 gap-6">
            <div class="space-y-4">
              <div class="flex items-center space-x-3">
                <Eye class="w-5 h-5 text-blue-600" />
                <span class="font-semibold text-gray-900">Akses Data</span>
              </div>
              <p class="text-gray-600 text-sm ml-8">
                Melihat semua data pribadi yang kami simpan tentang Anda
              </p>

              <div class="flex items-center space-x-3">
                <Edit class="w-5 h-5 text-green-600" />
                <span class="font-semibold text-gray-900">Koreksi Data</span>
              </div>
              <p class="text-gray-600 text-sm ml-8">
                Memperbarui atau memperbaiki informasi yang tidak akurat
              </p>
            </div>

            <div class="space-y-4">
              <div class="flex items-center space-x-3">
                <Trash2 class="w-5 h-5 text-red-600" />
                <span class="font-semibold text-gray-900">Hapus Data</span>
              </div>
              <p class="text-gray-600 text-sm ml-8">
                Menghapus akun dan semua data pribadi Anda secara permanen
              </p>

              <div class="flex items-center space-x-3">
                <Download class="w-5 h-5 text-purple-600" />
                <span class="font-semibold text-gray-900">Portabilitas Data</span>
              </div>
              <p class="text-gray-600 text-sm ml-8">
                Mengunduh data Anda dalam format yang dapat dibaca
              </p>
            </div>
          </div>
        </div>

        <!-- Contact -->
        <div class="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl text-white p-8 text-center">
          <h2 class="text-2xl font-bold mb-4">Ada Pertanyaan tentang Privasi?</h2>
          <p class="mb-6 opacity-90">
            Tim Privacy Officer kami siap membantu Anda memahami kebijakan ini
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <Button class="bg-white text-purple-600 hover:bg-gray-100 px-6 py-3">
              <Mail class="w-5 h-5 mr-2" />
              privacy@ringan.app
            </Button>
            <NuxtLink to="/hubungi-kami">
              <Button class="border-white text-white hover:bg-white hover:text-purple-600 px-6 py-3">
                <MessageCircle class="w-5 h-5 mr-2" />
                Hubungi Kami
              </Button>
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { 
  Shield, 
  Smartphone, 
  Heart, 
  Target, 
  Settings, 
  Lock, 
  Server, 
  AlertTriangle, 
  CheckCircle, 
  X, 
  Eye, 
  Edit, 
  Trash2, 
  Download, 
  Mail, 
  MessageCircle 
} from 'lucide-vue-next'

// Layout
definePageMeta({
  layout: 'default'
})

// Meta tags
useSeoMeta({
  title: 'Kebijakan Privasi - Ringan Mental Health App',
  description: 'Kebijakan privasi lengkap Ringan. Pelajari bagaimana kami melindungi dan menggunakan data pribadi Anda dengan standar keamanan tertinggi.',
})

// Reactive data
const lastUpdated = ref('15 Desember 2024')
</script>

<style scoped>
.container-custom {
  @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8;
}

.shadow-soft {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}
</style> 