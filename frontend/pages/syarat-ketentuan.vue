<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-green-50">
    <!-- Header -->
    <div class="bg-white shadow-sm">
      <div class="container-custom py-8">
        <div class="text-center">
          <h1 class="text-4xl font-bold text-gray-900 mb-4">
            Syarat & Ketentuan
          </h1>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto">
            Ketentuan penggunaan layanan Ringan yang perlu Anda ketahui
          </p>
          <p class="text-sm text-gray-500 mt-4">
            Terakhir diperbarui: {{ lastUpdated }}
          </p>
        </div>
      </div>
    </div>

    <!-- Terms Content -->
    <div class="container-custom py-16">
      <div class="max-w-4xl mx-auto space-y-8">
        
        <!-- Acceptance -->
        <div class="bg-white rounded-xl shadow-soft border border-gray-100 p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">1. Penerimaan Ketentuan</h2>
          <p class="text-gray-600 leading-relaxed">
            Dengan menggunakan aplikasi Ringan, Anda menyetujui untuk terikat dengan syarat dan ketentuan ini. 
            Jika Anda tidak menyetujui ketentuan ini, mohon untuk tidak menggunakan layanan kami.
          </p>
        </div>

        <!-- Service Description -->
        <div class="bg-white rounded-xl shadow-soft border border-gray-100 p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">2. Deskripsi Layanan</h2>
          <div class="space-y-4">
            <p class="text-gray-600 leading-relaxed">
              Ringan adalah platform kesehatan mental yang menyediakan:
            </p>
            <ul class="text-gray-600 space-y-2 ml-6">
              <li>• Konseling AI chatbot 24/7</li>
              <li>• Self-assessment kesehatan mental</li>
              <li>• Koneksi dengan psikolog profesional</li>
              <li>• Komunitas support dan artikel edukatif</li>
              <li>• Tools tracking mood dan progress</li>
            </ul>
          </div>
        </div>

        <!-- User Obligations -->
        <div class="bg-white rounded-xl shadow-soft border border-gray-100 p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">3. Kewajiban Pengguna</h2>
          <div class="space-y-4">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                <CheckCircle class="w-5 h-5 mr-2 text-green-600" />
                Yang Boleh Dilakukan
              </h3>
              <ul class="text-gray-600 space-y-1 ml-7">
                <li>• Menggunakan layanan untuk tujuan kesehatan mental pribadi</li>
                <li>• Berbagi pengalaman yang positif dan konstruktif</li>
                <li>• Memberikan feedback untuk perbaikan layanan</li>
              </ul>
            </div>

            <div>
              <h3 class="text-lg font-semibold text-gray-900 mb-2 flex items-center">
                <X class="w-5 h-5 mr-2 text-red-600" />
                Yang Dilarang
              </h3>
              <ul class="text-gray-600 space-y-1 ml-7">
                <li>• Menyalahgunakan platform untuk tujuan komersial</li>
                <li>• Mengunggah konten yang berbahaya atau tidak pantas</li>
                <li>• Melakukan reverse engineering terhadap aplikasi</li>
                <li>• Menggunakan data untuk tujuan di luar layanan</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Medical Disclaimer -->
        <div class="bg-yellow-50 border border-yellow-200 rounded-xl p-8">
          <h2 class="text-2xl font-bold text-yellow-800 mb-4 flex items-center">
            <AlertTriangle class="w-6 h-6 mr-2" />
            4. Disclaimer Medis
          </h2>
          <div class="space-y-4 text-yellow-700">
            <p class="leading-relaxed font-medium">
              PENTING: Layanan Ringan BUKAN pengganti diagnosis atau perawatan medis profesional.
            </p>
            <ul class="space-y-2 ml-4">
              <li>• AI chatbot memberikan dukungan emosional, bukan diagnosis medis</li>
              <li>• Self-assessment hanya untuk screening awal, bukan diagnosis resmi</li>
              <li>• Dalam situasi darurat, segera hubungi layanan darurat (119, 112)</li>
              <li>• Konsultasi dengan psikolog profesional tetap diperlukan untuk penanganan komprehensif</li>
            </ul>
          </div>
        </div>

        <!-- Privacy & Data -->
        <div class="bg-white rounded-xl shadow-soft border border-gray-100 p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">5. Privasi & Data</h2>
          <p class="text-gray-600 leading-relaxed">
            Penggunaan data pribadi Anda diatur dalam 
            <NuxtLink to="/kebijakan-privasi" class="text-purple-600 hover:text-purple-700 font-semibold">
              Kebijakan Privasi
            </NuxtLink> 
            kami. Dengan menggunakan layanan ini, Anda menyetujui pengumpulan dan penggunaan 
            data sesuai kebijakan tersebut.
          </p>
        </div>

        <!-- Limitation of Liability -->
        <div class="bg-white rounded-xl shadow-soft border border-gray-100 p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">6. Batasan Tanggung Jawab</h2>
          <div class="space-y-4 text-gray-600">
            <p class="leading-relaxed">
              Ringan tidak bertanggung jawab atas:
            </p>
            <ul class="space-y-2 ml-6">
              <li>• Kerugian yang timbul dari penggunaan informasi dalam aplikasi</li>
              <li>• Gangguan teknis atau downtime layanan</li>
              <li>• Tindakan atau saran dari psikolog partner (mereka bertanggung jawab independen)</li>
              <li>• Keputusan yang dibuat berdasarkan hasil assessment</li>
            </ul>
          </div>
        </div>

        <!-- Termination -->
        <div class="bg-white rounded-xl shadow-soft border border-gray-100 p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">7. Penghentian Layanan</h2>
          <div class="space-y-4 text-gray-600">
            <p class="leading-relaxed">
              Kami berhak menghentikan atau menangguhkan akses Anda jika:
            </p>
            <ul class="space-y-2 ml-6">
              <li>• Melanggar syarat dan ketentuan ini</li>
              <li>• Menggunakan layanan untuk tujuan yang merugikan</li>
              <li>• Mengganggu pengalaman pengguna lain</li>
            </ul>
            <p class="leading-relaxed mt-4">
              Anda dapat menghentikan penggunaan layanan kapan saja dengan menghapus akun Anda.
            </p>
          </div>
        </div>

        <!-- Changes to Terms -->
        <div class="bg-white rounded-xl shadow-soft border border-gray-100 p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">8. Perubahan Ketentuan</h2>
          <p class="text-gray-600 leading-relaxed">
            Kami dapat memperbarui syarat dan ketentuan ini sewaktu-waktu. Perubahan signifikan 
            akan diberitahukan melalui aplikasi atau email. Penggunaan berkelanjutan setelah 
            perubahan dianggap sebagai persetujuan terhadap ketentuan yang baru.
          </p>
        </div>

        <!-- Contact -->
        <div class="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl text-white p-8 text-center">
          <h2 class="text-2xl font-bold mb-4">Pertanyaan tentang Ketentuan?</h2>
          <p class="mb-6 opacity-90">
            Tim Legal kami siap membantu menjelaskan ketentuan ini
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <Button class="bg-white text-purple-600 hover:bg-gray-100 px-6 py-3">
              <Mail class="w-5 h-5 mr-2" />
              legal@ringan.app
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
import { CheckCircle, X, AlertTriangle, Mail, MessageCircle } from 'lucide-vue-next'

definePageMeta({
  layout: 'default'
})

useSeoMeta({
  title: 'Syarat & Ketentuan - Ringan Mental Health App',
  description: 'Syarat dan ketentuan penggunaan aplikasi Ringan. Pahami hak dan kewajiban Anda sebagai pengguna layanan kesehatan mental kami.',
})

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