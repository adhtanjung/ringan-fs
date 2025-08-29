<template>
  <div class="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-green-50">
    <!-- Header -->
    <div class="bg-white shadow-sm">
      <div class="container-custom py-8">
        <div class="text-center">
          <h1 class="text-4xl font-bold text-gray-900 mb-4">
            Hubungi Kami
          </h1>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto">
            Kami siap membantu Anda. Hubungi tim support Ringan kapan saja
          </p>
        </div>
      </div>
    </div>

    <!-- Contact Options -->
    <div class="container-custom py-16">
      <div class="max-w-6xl mx-auto">
        
        <!-- Emergency Section -->
        <div class="bg-red-50 border border-red-200 rounded-xl p-8 mb-12">
          <div class="text-center">
            <Phone class="w-12 h-12 text-red-600 mx-auto mb-4" />
            <h2 class="text-2xl font-bold text-red-800 mb-4">Bantuan Darurat 24/7</h2>
            <p class="text-red-700 mb-6">
              Jika Anda dalam kondisi darurat atau krisis mental, jangan ragu untuk segera menghubungi:
            </p>
            <div class="grid md:grid-cols-3 gap-4">
              <div class="bg-white p-4 rounded-lg border border-red-200">
                <h3 class="font-bold text-red-800">Hotline Bunuh Diri</h3>
                <p class="text-2xl font-bold text-red-600">119 ext 8</p>
              </div>
              <div class="bg-white p-4 rounded-lg border border-red-200">
                <h3 class="font-bold text-red-800">IGD Darurat</h3>
                <p class="text-2xl font-bold text-red-600">112</p>
              </div>
              <div class="bg-white p-4 rounded-lg border border-red-200">
                <h3 class="font-bold text-red-800">Crisis Text</h3>
                <p class="text-lg font-bold text-red-600">SMS "RINGAN"</p>
                <p class="text-sm text-red-600">ke 081234567890</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Contact Methods -->
        <div class="grid lg:grid-cols-2 gap-12 mb-16">
          
          <!-- Contact Info -->
          <div class="space-y-8">
            <h2 class="text-3xl font-bold text-gray-900 mb-8">Cara Menghubungi Kami</h2>
            
            <!-- Email Support -->
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <Mail class="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">Email Support</h3>
                <p class="text-gray-600 mb-2">Tim support kami akan membalas dalam 24 jam</p>
                <a href="mailto:support@ringan.app" class="text-purple-600 hover:text-purple-700 font-semibold">
                  support@ringan.app
                </a>
              </div>
            </div>

            <!-- WhatsApp -->
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <MessageCircle class="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">WhatsApp Support</h3>
                <p class="text-gray-600 mb-2">Chat langsung dengan tim support (Senin-Jumat, 9:00-18:00)</p>
                <a href="https://wa.me/628123456789" class="text-green-600 hover:text-green-700 font-semibold">
                  +62 812-3456-789
                </a>
              </div>
            </div>

            <!-- Live Chat -->
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <Zap class="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">Live Chat</h3>
                <p class="text-gray-600 mb-2">Chat real-time dalam aplikasi</p>
                <Button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 text-sm">
                  Buka Chat
                </Button>
              </div>
            </div>

            <!-- Office Address -->
            <div class="flex items-start space-x-4">
              <div class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <MapPin class="w-6 h-6 text-gray-600" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">Alamat Kantor</h3>
                <p class="text-gray-600">
                  Menara BCA, Lantai 15<br>
                  Jl. M.H. Thamrin No. 1<br>
                  Jakarta Pusat 10310<br>
                  Indonesia
                </p>
              </div>
            </div>
          </div>

          <!-- Contact Form -->
          <div class="bg-white rounded-xl shadow-soft border border-gray-100 p-8">
            <h3 class="text-2xl font-bold text-gray-900 mb-6">Kirim Pesan</h3>
            
            <form @submit.prevent="submitForm" class="space-y-6">
              <div class="grid md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Nama Lengkap</label>
                  <input 
                    v-model="form.name"
                    type="text" 
                    required
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="Masukkan nama Anda"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  <input 
                    v-model="form.email"
                    type="email" 
                    required
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    placeholder="email@example.com"
                  />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Kategori</label>
                <select 
                  v-model="form.category"
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="">Pilih kategori</option>
                  <option value="technical">Masalah Teknis</option>
                  <option value="account">Masalah Akun</option>
                  <option value="privacy">Privasi & Keamanan</option>
                  <option value="billing">Pembayaran</option>
                  <option value="feedback">Saran & Feedback</option>
                  <option value="partnership">Partnership</option>
                  <option value="other">Lainnya</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Subjek</label>
                <input 
                  v-model="form.subject"
                  type="text" 
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Ringkasan masalah atau pertanyaan"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Pesan</label>
                <textarea 
                  v-model="form.message"
                  required
                  rows="5"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Jelaskan pertanyaan atau masalah Anda secara detail..."
                ></textarea>
              </div>

              <Button 
                type="submit"
                :disabled="isSubmitting"
                class="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white py-3 px-6"
              >
                <Send class="w-5 h-5 mr-2" />
                {{ isSubmitting ? 'Mengirim...' : 'Kirim Pesan' }}
              </Button>
            </form>

            <!-- Success Message -->
            <div v-if="showSuccess" class="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div class="flex items-center">
                <CheckCircle class="w-5 h-5 text-green-600 mr-2" />
                <p class="text-green-800 font-medium">Pesan berhasil dikirim! Kami akan membalas dalam 24 jam.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- FAQ Section -->
        <div class="bg-white rounded-xl shadow-soft border border-gray-100 p-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-6 text-center">Pertanyaan yang Sering Ditanyakan</h2>
          <div class="grid md:grid-cols-2 gap-8">
            <div>
              <h3 class="font-semibold text-gray-900 mb-2">Berapa lama respon time support?</h3>
              <p class="text-gray-600 text-sm mb-4">
                Email: 24 jam, WhatsApp: 2-4 jam (jam kerja), Live Chat: Real-time
              </p>

              <h3 class="font-semibold text-gray-900 mb-2">Apakah konsultasi support gratis?</h3>
              <p class="text-gray-600 text-sm">
                Ya, semua support teknis dan pertanyaan umum gratis sepenuhnya.
              </p>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 mb-2">Bagaimana jika butuh bantuan di luar jam kerja?</h3>
              <p class="text-gray-600 text-sm mb-4">
                Gunakan email support atau live chat dalam aplikasi untuk mendapat bantuan otomatis.
              </p>

              <h3 class="font-semibold text-gray-900 mb-2">Ada pertanyaan lebih banyak?</h3>
              <p class="text-gray-600 text-sm">
                Kunjungi halaman <NuxtLink to="/faq" class="text-purple-600 hover:text-purple-700 font-semibold">FAQ</NuxtLink> 
                untuk jawaban lengkap.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { 
  Phone, 
  Mail, 
  MessageCircle, 
  Zap, 
  MapPin, 
  Send, 
  CheckCircle 
} from 'lucide-vue-next'

definePageMeta({
  layout: 'default'
})

useSeoMeta({
  title: 'Hubungi Kami - Ringan Mental Health App',
  description: 'Hubungi tim support Ringan untuk bantuan, pertanyaan, atau feedback. Kami siap membantu Anda 24/7 melalui berbagai channel komunikasi.',
})

// Form data
const form = ref({
  name: '',
  email: '',
  category: '',
  subject: '',
  message: ''
})

const isSubmitting = ref(false)
const showSuccess = ref(false)

// Submit form
const submitForm = async () => {
  isSubmitting.value = true
  
  // Simulate form submission
  setTimeout(() => {
    isSubmitting.value = false
    showSuccess.value = true
    
    // Reset form
    form.value = {
      name: '',
      email: '',
      category: '',
      subject: '',
      message: ''
    }
    
    // Hide success message after 5 seconds
    setTimeout(() => {
      showSuccess.value = false
    }, 5000)
  }, 1000)
}
</script>

<style scoped>
.container-custom {
  @apply max-w-7xl mx-auto px-4 sm:px-6 lg:px-8;
}

.shadow-soft {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}
</style> 