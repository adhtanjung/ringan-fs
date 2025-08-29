<template>
	<div
		class="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-green-50"
	>
		<!-- Header -->
		<header class="bg-white shadow-sm border-b">
			<div class="container-custom py-4">
				<div class="flex items-center justify-between">
					<div class="flex items-center space-x-4">
						<NuxtLink to="/" class="flex items-center space-x-2">
							<div
								class="w-8 h-8 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center"
							>
								<Heart class="w-4 h-4 text-white" />
							</div>
							<span class="text-xl font-bold text-gray-900">Ringan</span>
						</NuxtLink>
						<div class="hidden md:block w-px h-6 bg-gray-300"></div>
						<span class="hidden md:block text-sm text-gray-600"
							>Demo Interaktif</span
						>
					</div>
					<NuxtLink
						to="/"
						class="text-sm text-gray-600 hover:text-gray-900 flex items-center"
					>
						<ArrowLeft class="w-4 h-4 mr-1" />
						Kembali ke Beranda
					</NuxtLink>
				</div>
			</div>
		</header>

		<div class="container-custom section-padding">
			<div class="max-w-4xl mx-auto">
				<!-- Demo Header -->
				<div class="text-center mb-8">
					<h1 class="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
						Demo <span class="gradient-text">Interaktif</span> Ringan AI
					</h1>
					<p class="text-lg text-gray-600 max-w-2xl mx-auto">
						Rasakan pengalaman berbicara dengan AI assistant yang peduli
						kesehatan mentalmu
					</p>
				</div>

				<!-- Name Input Screen -->
				<div v-if="!userName" class="max-w-md mx-auto">
					<div class="bg-white rounded-2xl shadow-soft p-8 text-center">
						<div
							class="w-20 h-20 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-6"
						>
							<Bot class="w-10 h-10 text-white" />
						</div>
						<h2 class="text-2xl font-bold text-gray-900 mb-4">
							Halo! Kenalan yuk!
						</h2>
						<p class="text-gray-600 mb-6">
							Sebelum kita mulai ngobrol, boleh tau nama kamu? Biar aku bisa
							panggil dengan nama yang tepat 😊
						</p>
						<div class="space-y-4">
							<input
								v-model="nameInput"
								@keypress.enter="startChat"
								type="text"
								placeholder="Masukkan nama kamu..."
								class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-center"
								maxlength="50"
							/>
							<button
								@click="startChat"
								:disabled="!nameInput.trim()"
								class="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold py-3 rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
							>
								Mulai Ngobrol
							</button>
						</div>
						<p class="text-xs text-gray-500 mt-4">
							Tenang, data kamu aman dan ini hanya demo 🔒
						</p>
					</div>
				</div>

				<!-- Main Chat Interface -->
				<div v-else class="grid lg:grid-cols-3 gap-8">
					<!-- Chat Interface -->
					<div class="lg:col-span-2">
						<!-- Mode Toggle -->
						<div class="mb-6">
							<div class="bg-white rounded-2xl p-4 shadow-soft">
								<div class="flex items-center justify-center space-x-2">
									<button
										@click="activeMode = 'text'"
										:class="[
											'flex items-center space-x-2 px-3 py-2 rounded-lg font-medium transition-all text-sm',
											activeMode === 'text'
												? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white'
												: 'text-gray-600 hover:bg-gray-100',
										]"
									>
										<MessageSquare class="w-4 h-4" />
										<span>Chat Teks</span>
									</button>
									<button
										@click="activeMode = 'stream'"
										:class="[
											'flex items-center space-x-2 px-3 py-2 rounded-lg font-medium transition-all text-sm',
											activeMode === 'stream'
												? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white'
												: 'text-gray-600 hover:bg-gray-100',
										]"
									>
										<Zap class="w-4 h-4" />
										<span>Chat Stream</span>
									</button>
									<button
										@click="activeMode = 'voice'"
										:class="[
											'flex items-center space-x-2 px-3 py-2 rounded-lg font-medium transition-all text-sm',
											activeMode === 'voice'
												? 'bg-gradient-to-r from-green-500 to-blue-500 text-white'
												: 'text-gray-600 hover:bg-gray-100',
										]"
										:disabled="!isSpeechSupported"
									>
										<Volume2 class="w-4 h-4" />
										<span>Suara Custom</span>
										<span
											v-if="!isSpeechSupported"
											class="text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full ml-1"
										>
											Tidak Didukung
										</span>
									</button>
									<button
										@click="activeMode = 'convai'"
										:class="[
											'flex items-center space-x-2 px-3 py-2 rounded-lg font-medium transition-all text-sm',
											activeMode === 'convai'
												? 'bg-gradient-to-r from-orange-500 to-red-500 text-white'
												: 'text-gray-600 hover:bg-gray-100',
										]"
									>
										<Zap class="w-4 h-4" />
										<span>ConvAI Widget</span>
									</button>
								</div>
							</div>
						</div>

						<!-- Text Chat Interface -->
						<div
							v-if="activeMode === 'text'"
							class="bg-white rounded-2xl shadow-soft overflow-hidden"
						>
							<!-- Chat Header -->
							<div
								class="bg-gradient-to-r from-purple-600 to-blue-600 p-4 text-white"
							>
								<div class="flex items-center justify-between">
									<div class="flex items-center">
										<div
											class="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-3"
										>
											<Bot class="w-5 h-5 text-white" />
										</div>
										<div>
											<h3 class="font-semibold">Ringan AI - Chat Teks</h3>
											<div class="flex items-center text-sm opacity-90">
												<div
													class="w-2 h-2 bg-green-400 rounded-full mr-2"
												></div>
												Online - Siap mendengarkan {{ userName }}
											</div>
										</div>
									</div>
									<button
										@click="resetDemo"
										class="text-white opacity-75 hover:opacity-100 text-sm"
									>
										Reset Demo
									</button>
								</div>
							</div>

							<!-- Chat Messages -->
							<div
								class="h-96 overflow-y-auto p-4 space-y-4"
								ref="chatContainer"
							>
								<div
									v-for="message in ollamaMessages"
									:key="message.id"
									class="animate-fade-in"
								>
									<!-- AI Message -->
									<div
										v-if="message.sender === 'ai'"
										class="flex items-start space-x-3"
									>
										<div
											class="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center flex-shrink-0"
										>
											<Bot class="w-4 h-4 text-white" />
										</div>
										<div
											class="bg-gray-100 rounded-2xl rounded-tl-md p-4 max-w-sm"
										>
											<div
												class="text-gray-800 prose prose-sm max-w-none"
												v-html="message.text"
											></div>
											<span class="text-xs text-gray-500 mt-1 block">{{
												message.time
											}}</span>
										</div>
									</div>

									<!-- User Message -->
									<div v-else class="flex items-start space-x-3 justify-end">
										<div
											class="bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-2xl rounded-tr-md p-4 max-w-sm"
										>
											<p class="text-sm">{{ message.text }}</p>
											<span class="text-xs text-purple-100 mt-1 block">{{
												message.time
											}}</span>
										</div>
										<div
											class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0"
										>
											<User class="w-4 h-4 text-gray-600" />
										</div>
									</div>
								</div>

								<!-- Typing Indicator -->
								<div
									v-if="isProcessing"
									class="flex items-start space-x-3 animate-pulse"
								>
									<div
										class="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center flex-shrink-0"
									>
										<Bot class="w-4 h-4 text-white" />
									</div>
									<div class="bg-gray-100 rounded-2xl rounded-tl-md p-4">
										<div class="flex space-x-1">
											<div
												class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
											></div>
											<div
												class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
												style="animation-delay: 0.1s"
											></div>
											<div
												class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
												style="animation-delay: 0.2s"
											></div>
										</div>
									</div>
								</div>
							</div>

							<!-- Quick Response Buttons -->
							<div v-if="showQuickResponses" class="px-4 pb-4">
								<div class="flex flex-wrap gap-2">
									<button
										v-for="response in quickResponses"
										:key="response"
										@click="sendQuickResponse(response)"
										class="px-3 py-2 bg-purple-100 text-purple-700 rounded-full text-sm hover:bg-purple-200 transition-colors cursor-pointer"
									>
										{{ response }}
									</button>
								</div>
							</div>

							<!-- Chat Input -->
							<div class="border-t p-4">
								<div
									v-if="isChatLimitReached && showRegistrationCTA"
									class="mb-4 p-4 bg-gradient-to-r from-purple-100 to-blue-100 rounded-lg border border-purple-200"
								>
									<div class="text-center">
										<h3 class="font-bold text-purple-800 mb-2">
											🎉 Demo Selesai!
										</h3>
										<p class="text-sm text-purple-700 mb-3">
											Kamu sudah mencoba {{ maxChats }} percakapan. Untuk
											melanjutkan tanpa batas:
										</p>
										<div class="flex flex-col sm:flex-row gap-2">
											<button
												class="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold py-2 px-4 rounded-lg hover:shadow-lg transition-all"
											>
												📱 Download Aplikasi
											</button>
											<button
												@click="resetDemo"
												class="flex-1 bg-white text-purple-600 border border-purple-300 font-semibold py-2 px-4 rounded-lg hover:bg-purple-50 transition-all"
											>
												🔄 Coba Lagi
											</button>
										</div>
									</div>
								</div>

								<div class="flex space-x-3">
									<input
										v-model="currentInput"
										@keypress.enter="sendLocalMessage"
										:disabled="isProcessing || isChatLimitReached"
										type="text"
										:placeholder="
											isChatLimitReached
												? 'Demo telah selesai...'
												: 'Ketik perasaanmu...'
										"
										class="flex-1 border border-gray-300 rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
									/>
									<button
										@click="sendLocalMessage"
										:disabled="
											isProcessing || !currentInput.trim() || isChatLimitReached
										"
										class="w-10 h-10 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-full flex items-center justify-center hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
									>
										<Send class="w-4 h-4" />
									</button>
								</div>
							</div>
						</div>

						<!-- Streaming Chat Interface -->
						<div
							v-else-if="activeMode === 'stream'"
							class="bg-white rounded-2xl shadow-soft overflow-hidden"
						>
							<!-- Chat Header -->
							<div
								class="bg-gradient-to-r from-cyan-600 to-blue-600 p-4 text-white"
							>
								<div class="flex items-center justify-between">
									<div class="flex items-center">
										<div
											class="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-3"
										>
											<Zap class="w-5 h-5 text-white" />
										</div>
										<div>
											<h3 class="font-semibold">Ringan AI - Chat Stream</h3>
											<div class="flex items-center text-sm opacity-90">
												<div
													:class="[
														'w-2 h-2 rounded-full mr-2',
														isConnected ? 'bg-green-400' : 'bg-red-400',
													]"
												></div>
												{{ isConnected ? "Terhubung" : "Terputus" }} - WebSocket
												Real-time
											</div>
										</div>
									</div>
									<div class="flex items-center space-x-2">
										<span
											class="text-xs bg-white bg-opacity-20 px-2 py-1 rounded-full"
										>
											Session: {{ sessionId.slice(-8) }}
										</span>
										<button
											@click="resetDemo"
											class="text-white opacity-75 hover:opacity-100 text-sm"
										>
											Reset Demo
										</button>
									</div>
								</div>
							</div>

							<!-- Chat Messages -->
							<div
								class="h-96 overflow-y-auto p-4 space-y-4"
								ref="streamChatContainer"
							>
								<div
									v-for="message in streamMessages"
									:key="message.id"
									class="animate-fade-in"
								>
									<!-- AI Message -->
									<div
										v-if="message.sender === 'ai'"
										class="flex items-start space-x-3"
									>
										<div
											class="w-8 h-8 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full flex items-center justify-center flex-shrink-0"
										>
											<Zap class="w-4 h-4 text-white" />
										</div>
										<div
											class="bg-gray-100 rounded-2xl rounded-tl-md p-4 max-w-sm"
										>
											<div
												class="text-gray-800 prose prose-sm max-w-none"
												v-html="message.text"
											></div>
											<span class="text-xs text-gray-500 mt-1 block">{{
												message.time
											}}</span>
										</div>
									</div>

									<!-- User Message -->
									<div v-else class="flex items-start space-x-3 justify-end">
										<div
											class="bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-2xl rounded-tr-md p-4 max-w-sm"
										>
											<p class="text-sm">{{ message.text }}</p>
											<span class="text-xs text-cyan-100 mt-1 block">{{
												message.time
											}}</span>
										</div>
										<div
											class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0"
										>
											<User class="w-4 h-4 text-gray-600" />
										</div>
									</div>
								</div>

								<!-- Streaming Indicator -->
								<div v-if="isStreaming" class="flex items-start space-x-3">
									<div
										class="w-8 h-8 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full flex items-center justify-center flex-shrink-0"
									>
										<Zap class="w-4 h-4 text-white animate-pulse" />
									</div>
									<div
										class="bg-gray-100 rounded-2xl rounded-tl-md p-4 max-w-sm"
									>
										<div class="flex items-center space-x-2">
											<div class="flex space-x-1">
												<div
													class="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"
												></div>
												<div
													class="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"
													style="animation-delay: 0.1s"
												></div>
												<div
													class="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"
													style="animation-delay: 0.2s"
												></div>
											</div>
											<span class="text-xs text-gray-500">Streaming...</span>
										</div>
									</div>
								</div>
							</div>

							<!-- Connection Status -->
							<div v-if="!isConnected || streamError" class="px-4 pb-2">
								<div
									v-if="!isConnected"
									class="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-2"
								>
									<div class="flex items-center space-x-2">
										<div
											class="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"
										></div>
										<span class="text-sm text-yellow-700"
											>WebSocket terputus. Akan menggunakan HTTP API sebagai
											fallback...</span
										>
									</div>
								</div>
								<div
									v-if="streamError"
									class="bg-red-50 border border-red-200 rounded-lg p-3"
								>
									<div class="flex items-center justify-between">
										<div class="flex items-center space-x-2">
											<div class="w-2 h-2 bg-red-500 rounded-full"></div>
											<span class="text-sm text-red-700">{{
												streamError
											}}</span>
										</div>
										<button
											@click="clearStreamError"
											class="text-red-500 hover:text-red-700 text-xs"
										>
											✕
										</button>
									</div>
								</div>
							</div>

							<!-- Chat Input -->
							<div class="border-t p-4">
								<div class="flex space-x-3">
									<input
										v-model="streamInput"
										@keypress.enter="sendStreamMessage"
										:disabled="isStreaming || !isConnected"
										type="text"
										:placeholder="
											!isConnected
												? 'Menghubungkan...'
												: isStreaming
												? 'Menunggu respons...'
												: 'Ketik perasaanmu...'
										"
										class="flex-1 border border-gray-300 rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
									/>
									<button
										@click="sendStreamMessage"
										:disabled="
											isStreaming || !streamInput.trim() || !isConnected
										"
										class="w-10 h-10 bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-full flex items-center justify-center hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
									>
										<Send class="w-4 h-4" />
									</button>
								</div>
							</div>
						</div>

						<!-- Voice Chat Interface -->
						<div
							v-else-if="activeMode === 'voice'"
							class="bg-white rounded-2xl shadow-soft overflow-hidden"
						>
							<!-- Voice Chat Header -->
							<div
								class="bg-gradient-to-r from-green-600 to-blue-600 p-4 text-white"
							>
								<div class="flex items-center justify-between">
									<div class="flex items-center">
										<div
											class="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-3"
										>
											<Volume2 class="w-5 h-5 text-white" />
										</div>
										<div>
											<h3 class="font-semibold">
												Ringan AI - Percakapan Suara
											</h3>
											<div class="flex items-center text-sm opacity-90">
												<div
													class="w-2 h-2 bg-green-400 rounded-full mr-2"
												></div>
												{{
													isVoiceConversationActive
														? isFluidMode
															? "Mode Fluid"
															: "Aktif"
														: "Tidak Aktif"
												}}
												- {{ userName }}
												<span
													v-if="isTestScriptMode"
													class="ml-2 bg-yellow-400 text-yellow-900 px-2 py-1 rounded-full text-xs font-medium"
												>
													Test Script
												</span>
											</div>
										</div>
									</div>
									<div class="flex items-center space-x-2">
										<!-- Mute Button -->
										<button
											v-if="isVoiceConversationActive"
											@click="toggleMute"
											:class="[
												'flex items-center space-x-1 px-3 py-1 rounded-lg text-xs font-medium transition-all',
												isMuted
													? 'bg-red-500 bg-opacity-20 text-red-100 border border-red-400'
													: 'bg-white bg-opacity-20 text-white border border-white border-opacity-30',
											]"
										>
											<Volume2 v-if="!isMuted" class="w-3 h-3" />
											<VolumeX v-else class="w-3 h-3" />
											<span>{{ isMuted ? "Muted" : "Audio" }}</span>
										</button>

										<!-- Fluid Mode Toggle -->
										<button
											@click="toggleFluidMode"
											:class="[
												'flex items-center space-x-1 px-3 py-1 rounded-lg text-xs font-medium transition-all',
												isFluidMode
													? 'bg-yellow-400 bg-opacity-20 text-yellow-100 border border-yellow-400'
													: 'bg-white bg-opacity-20 text-white border border-white border-opacity-30',
											]"
										>
											<Zap class="w-3 h-3" />
											<span>{{ isFluidMode ? "Fluid ON" : "Manual" }}</span>
										</button>

										<button
											@click="stopVoiceConversation"
											v-if="isVoiceConversationActive"
											class="text-white opacity-75 hover:opacity-100 text-sm"
										>
											Stop Suara
										</button>
									</div>
								</div>
							</div>

							<!-- Fluid Mode Info Banner -->
							<div
								v-if="isVoiceConversationActive && isFluidMode"
								class="bg-gradient-to-r from-yellow-50 to-orange-50 border-b border-yellow-200 p-3"
							>
								<div class="flex items-center justify-between text-sm">
									<div class="flex items-center space-x-2">
										<Zap class="w-4 h-4 text-yellow-600" />
										<span class="font-medium text-yellow-800"
											>Mode Fluid Aktif</span
										>
										<span class="text-yellow-600"
											>- Percakapan otomatis hingga
											{{ maxFluidConversations }} kali</span
										>
									</div>
									<div class="text-yellow-700 font-medium">
										{{ conversationCount }}/{{ maxFluidConversations }}
										percakapan
									</div>
								</div>
								<div class="mt-2 w-full bg-yellow-200 rounded-full h-1">
									<div
										class="bg-yellow-500 h-1 rounded-full transition-all duration-300"
										:style="{
											width: `${
												(conversationCount / maxFluidConversations) * 100
											}%`,
										}"
									></div>
								</div>
							</div>

							<!-- Voice Chat Messages -->
							<div
								class="h-96 overflow-y-auto p-4 space-y-4"
								ref="voiceChatContainer"
							>
								<div
									v-if="!isVoiceConversationActive"
									class="text-center py-16"
								>
									<div
										class="w-20 h-20 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4"
									>
										<Volume2 class="w-10 h-10 text-white" />
									</div>
									<h3 class="text-xl font-bold text-gray-900 mb-2">
										Percakapan Suara
									</h3>
									<p class="text-gray-600 mb-6 max-w-md mx-auto">
										Mulai percakapan suara dengan Ringan AI. Pilih mode manual
										atau fluid untuk pengalaman yang berbeda.
									</p>

									<!-- Mode Selection -->
									<div class="mb-6 flex justify-center space-x-4">
										<button
											@click="isFluidMode = false"
											:class="[
												'px-4 py-2 rounded-lg border-2 transition-all text-sm font-medium',
												!isFluidMode
													? 'border-green-500 bg-green-50 text-green-700'
													: 'border-gray-300 text-gray-600 hover:border-green-300',
											]"
										>
											🎙️ Manual Mode
											<div class="text-xs mt-1 opacity-75">
												Klik untuk bicara
											</div>
										</button>

										<button
											@click="isFluidMode = true"
											:class="[
												'px-4 py-2 rounded-lg border-2 transition-all text-sm font-medium',
												isFluidMode
													? 'border-yellow-500 bg-yellow-50 text-yellow-700'
													: 'border-gray-300 text-gray-600 hover:border-yellow-300',
											]"
										>
											⚡ Fluid Mode
											<div class="text-xs mt-1 opacity-75">
												Otomatis + test script
											</div>
										</button>
									</div>

									<div class="flex flex-col space-y-3">
										<button
											@click="startVoiceConversation"
											:disabled="!isSpeechSupported"
											class="bg-gradient-to-r from-green-600 to-blue-600 text-white font-semibold py-3 px-6 rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
										>
											🎙️ Mulai Percakapan Suara
										</button>
										<button
											@click="startFullscreenVoiceMode"
											:disabled="!isSpeechSupported"
											class="bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-3 px-6 rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
										>
											🖥️ Mode Layar Penuh
										</button>
									</div>
									<p
										v-if="!isSpeechSupported"
										class="text-sm text-red-600 mt-2"
									>
										Speech recognition tidak didukung di browser ini
									</p>
								</div>

								<!-- Main Conversation Messages -->
								<div v-else-if="!isTestScriptMode">
									<div
										v-for="message in voiceMessages"
										:key="message.text + message.time"
										class="animate-fade-in"
									>
										<!-- AI Voice Message -->
										<div
											v-if="message.sender === 'ai'"
											class="flex items-start space-x-3"
										>
											<div
												class="w-8 h-8 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center flex-shrink-0"
											>
												<Volume2 class="w-4 h-4 text-white" />
											</div>
											<div
												class="bg-green-50 rounded-2xl rounded-tl-md p-4 max-w-sm"
											>
												<p class="text-gray-800 text-sm">{{ message.text }}</p>
												<span class="text-xs text-gray-500 mt-1 block">{{
													message.time
												}}</span>
											</div>
										</div>

										<!-- User Voice Message -->
										<div v-else class="flex items-start space-x-3 justify-end">
											<div
												class="bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-2xl rounded-tr-md p-4 max-w-sm"
											>
												<p class="text-sm">{{ message.text }}</p>
												<span class="text-xs text-green-100 mt-1 block">{{
													message.time
												}}</span>
											</div>
											<div
												class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0"
											>
												<User class="w-4 h-4 text-gray-600" />
											</div>
										</div>
									</div>

									<!-- Processing Indicator -->
									<div
										v-if="isProcessingVoice || isTTSGenerating"
										class="flex items-start space-x-3 animate-pulse"
									>
										<div
											class="w-8 h-8 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center flex-shrink-0"
										>
											<Volume2 class="w-4 h-4 text-white" />
										</div>
										<div class="bg-green-50 rounded-2xl rounded-tl-md p-4">
											<div class="flex space-x-1">
												<div
													class="w-2 h-2 bg-green-400 rounded-full animate-bounce"
												></div>
												<div
													class="w-2 h-2 bg-green-400 rounded-full animate-bounce"
													style="animation-delay: 0.1s"
												></div>
												<div
													class="w-2 h-2 bg-green-400 rounded-full animate-bounce"
													style="animation-delay: 0.2s"
												></div>
											</div>
										</div>
									</div>
								</div>

								<!-- Test Script Messages -->
								<div v-else>
									<div
										class="mb-4 p-3 bg-gradient-to-r from-yellow-100 to-orange-100 rounded-lg border border-yellow-300"
									>
										<div class="flex items-center space-x-2 text-yellow-800">
											<User class="w-4 h-4" />
											<span class="font-medium text-sm"
												>Sesi Evaluasi Test Script</span
											>
										</div>
										<p class="text-xs text-yellow-700 mt-1">
											Jawab pertanyaan berikut untuk memberikan feedback tentang
											pengalaman kamu
										</p>
									</div>

									<div
										v-for="message in testScriptMessages"
										:key="message.text + message.time"
										class="animate-fade-in"
									>
										<!-- AI Test Question -->
										<div
											v-if="message.sender === 'ai'"
											class="flex items-start space-x-3"
										>
											<div
												class="w-8 h-8 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full flex items-center justify-center flex-shrink-0"
											>
												<User class="w-4 h-4 text-white" />
											</div>
											<div
												class="bg-yellow-50 rounded-2xl rounded-tl-md p-4 max-w-sm border border-yellow-200"
											>
												<p class="text-gray-800 text-sm font-medium">
													{{ message.text }}
												</p>
												<span class="text-xs text-gray-500 mt-1 block">{{
													message.time
												}}</span>
											</div>
										</div>

										<!-- User Test Answer -->
										<div v-else class="flex items-start space-x-3 justify-end">
											<div
												class="bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-2xl rounded-tr-md p-4 max-w-sm"
											>
												<p class="text-sm">{{ message.text }}</p>
												<span class="text-xs text-yellow-100 mt-1 block">{{
													message.time
												}}</span>
											</div>
											<div
												class="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0"
											>
												<User class="w-4 h-4 text-gray-600" />
											</div>
										</div>
									</div>

									<!-- Test Script Processing Indicator -->
									<div
										v-if="isProcessingVoice || isTTSGenerating"
										class="flex items-start space-x-3 animate-pulse"
									>
										<div
											class="w-8 h-8 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full flex items-center justify-center flex-shrink-0"
										>
											<User class="w-4 h-4 text-white" />
										</div>
										<div
											class="bg-yellow-50 rounded-2xl rounded-tl-md p-4 border border-yellow-200"
										>
											<div class="flex space-x-1">
												<div
													class="w-2 h-2 bg-yellow-400 rounded-full animate-bounce"
												></div>
												<div
													class="w-2 h-2 bg-yellow-400 rounded-full animate-bounce"
													style="animation-delay: 0.1s"
												></div>
												<div
													class="w-2 h-2 bg-yellow-400 rounded-full animate-bounce"
													style="animation-delay: 0.2s"
												></div>
											</div>
										</div>
									</div>
								</div>
							</div>

							<!-- Voice Controls -->
							<div v-if="isVoiceConversationActive" class="border-t p-4">
								<div
									v-if="!isFluidMode || isTestScriptMode"
									class="flex justify-center space-x-4"
								>
									<button
										@click="startVoiceInput(true)"
										:disabled="
											isListening || isProcessingVoice || isTTSGenerating
										"
										:class="[
											'flex items-center space-x-2 px-6 py-3 rounded-full font-semibold transition-all',
											isListening
												? 'bg-red-500 text-white'
												: 'bg-gradient-to-r from-green-600 to-blue-600 text-white hover:shadow-lg',
											(isProcessingVoice || isTTSGenerating) &&
												'opacity-50 cursor-not-allowed',
										]"
									>
										<Mic v-if="!isListening" class="w-5 h-5" />
										<MicOff v-else class="w-5 h-5" />
										<span v-if="!isListening">{{
											isTestScriptMode
												? "Jawab Pertanyaan"
												: "Tekan untuk Bicara"
										}}</span>
										<span v-else>Sedang Mendengarkan...</span>
									</button>

									<button
										v-if="isListening"
										@click="stopListening"
										class="flex items-center space-x-2 px-6 py-3 bg-gray-500 text-white rounded-full font-semibold hover:bg-gray-600 transition-all"
									>
										<MicOff class="w-5 h-5" />
										<span>Stop</span>
									</button>

									<button
										@click="startFullscreenVoiceMode"
										:disabled="
											isListening || isProcessingVoice || isTTSGenerating
										"
										class="flex items-center space-x-2 px-4 py-3 bg-purple-600 text-white rounded-full font-semibold hover:bg-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
									>
										<span>🖥️</span>
										<span class="hidden sm:inline">Layar Penuh</span>
									</button>
								</div>

								<!-- Fluid Mode Status -->
								<div v-else class="text-center space-y-3">
									<div
										class="bg-green-50 rounded-lg p-4 border border-green-200"
									>
										<div
											class="flex items-center justify-center space-x-2 text-green-700 mb-2"
										>
											<Zap class="w-5 h-5" />
											<span class="font-medium">Mode Fluid Aktif</span>
										</div>
										<p class="text-sm text-green-600 mb-3">
											{{
												isListening
													? "Sedang mendengarkan..."
													: "Berbicara otomatis - tidak perlu klik tombol!"
											}}
										</p>
										<div
											v-if="isListening"
											class="flex justify-center space-x-1"
										>
											<div
												class="w-2 h-2 bg-green-500 rounded-full animate-bounce"
											></div>
											<div
												class="w-2 h-2 bg-green-500 rounded-full animate-bounce"
												style="animation-delay: 0.1s"
											></div>
											<div
												class="w-2 h-2 bg-green-500 rounded-full animate-bounce"
												style="animation-delay: 0.2s"
											></div>
										</div>
									</div>

									<button
										@click="startFullscreenVoiceMode"
										class="bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-2 px-4 rounded-lg hover:shadow-lg transition-all text-sm"
									>
										🖥️ Beralih ke Layar Penuh
									</button>
								</div>
							</div>
						</div>

						<!-- Fullscreen Voice Mode -->
						<div
							v-if="isFullscreenVoiceMode"
							class="fixed inset-0 bg-gradient-to-br from-green-900 via-blue-900 to-purple-900 z-50 flex flex-col"
						>
							<!-- Fullscreen Voice Header -->
							<div class="bg-black bg-opacity-20 p-3 lg:p-4 flex-shrink-0">
								<div class="flex items-center justify-between">
									<div class="flex items-center space-x-2 lg:space-x-3">
										<div
											class="w-10 h-10 lg:w-12 lg:h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center"
										>
											<Volume2 class="w-5 h-5 lg:w-6 lg:h-6 text-white" />
										</div>
										<div class="text-white">
											<h1 class="font-bold text-base lg:text-lg">
												Ringan AI - Mode Suara
											</h1>
											<p class="text-xs lg:text-sm opacity-75">
												{{ isFluidMode ? "Mode Fluid Aktif" : "Mode Manual" }} -
												{{ userName }}
												{{
													isListening
														? "- Mendengarkan"
														: isProcessingVoice
														? "- Memproses"
														: "- Siap"
												}}
											</p>
										</div>
									</div>

									<div class="flex items-center space-x-1 lg:space-x-2">
										<!-- Mute Button -->
										<button
											@click="toggleMute"
											:class="[
												'flex items-center space-x-1 px-2 lg:px-3 py-1 lg:py-2 rounded-lg text-xs font-medium transition-all',
												isMuted
													? 'bg-red-500 bg-opacity-30 text-red-200 border border-red-400'
													: 'bg-white bg-opacity-20 text-white border border-white border-opacity-30',
											]"
										>
											<Volume2 v-if="!isMuted" class="w-3 h-3 lg:w-4 lg:h-4" />
											<VolumeX v-else class="w-3 h-3 lg:w-4 lg:h-4" />
											<span class="hidden sm:inline">{{
												isMuted ? "Muted" : "Audio"
											}}</span>
										</button>

										<!-- Fluid Mode Toggle -->
										<button
											@click="toggleFluidMode"
											:class="[
												'flex items-center space-x-1 px-2 lg:px-3 py-1 lg:py-2 rounded-lg text-xs font-medium transition-all',
												isFluidMode
													? 'bg-yellow-500 bg-opacity-30 text-yellow-200 border border-yellow-400'
													: 'bg-white bg-opacity-20 text-white border border-white border-opacity-30',
											]"
										>
											<Zap class="w-3 h-3 lg:w-4 lg:h-4" />
											<span class="hidden sm:inline">{{
												isFluidMode ? "Fluid ON" : "Manual"
											}}</span>
										</button>

										<!-- Close Fullscreen -->
										<button
											@click="endFullscreenVoiceMode"
											class="text-white opacity-75 hover:opacity-100 text-xs lg:text-sm flex items-center space-x-1"
										>
											<X class="w-3 h-3 lg:w-4 lg:h-4" />
											<span class="hidden sm:inline">Selesai</span>
										</button>
									</div>
								</div>

								<!-- Fluid Mode Progress -->
								<div v-if="isFluidMode" class="mt-2 lg:mt-3">
									<div
										class="flex items-center justify-between text-xs lg:text-sm text-white"
									>
										<span>Percakapan Otomatis</span>
										<span
											>{{ conversationCount }}/{{ maxFluidConversations }}</span
										>
									</div>
									<div
										class="mt-1 w-full bg-white bg-opacity-20 rounded-full h-1"
									>
										<div
											class="bg-yellow-400 h-1 rounded-full transition-all duration-300"
											:style="{
												width: `${
													(conversationCount / maxFluidConversations) * 100
												}%`,
											}"
										></div>
									</div>
								</div>
							</div>

							<!-- Main Fullscreen Voice Interface -->
							<div
								class="flex-1 flex flex-col items-center justify-center p-4 lg:p-8"
							>
								<!-- Central Audio Visualizer -->
								<div class="mb-6 lg:mb-8">
									<div
										:class="[
											'w-24 h-24 lg:w-32 lg:h-32 rounded-full flex items-center justify-center transition-all duration-300',
											isListening
												? 'bg-red-500 bg-opacity-30 border-4 border-red-400 animate-pulse'
												: isProcessingVoice || isTTSGenerating
												? 'bg-blue-500 bg-opacity-30 border-4 border-blue-400 animate-bounce'
												: 'bg-white bg-opacity-20 border-4 border-white border-opacity-30',
										]"
									>
										<div
											:class="[
												'w-16 h-16 lg:w-20 lg:h-20 rounded-full flex items-center justify-center transition-all',
												isListening
													? 'bg-red-500'
													: isProcessingVoice || isTTSGenerating
													? 'bg-blue-500'
													: 'bg-green-500',
											]"
										>
											<Mic
												v-if="isListening"
												class="w-8 h-8 lg:w-10 lg:h-10 text-white"
											/>
											<Bot
												v-else-if="isProcessingVoice || isTTSGenerating"
												class="w-8 h-8 lg:w-10 lg:h-10 text-white"
											/>
											<Volume2
												v-else
												class="w-8 h-8 lg:w-10 lg:h-10 text-white"
											/>
										</div>
									</div>
								</div>

								<!-- Status Text -->
								<div class="text-center text-white mb-6 lg:mb-8 px-4">
									<h2 class="text-lg lg:text-2xl font-bold mb-2">
										{{
											isListening
												? "🎙️ Sedang Mendengarkan..."
												: isProcessingVoice
												? "🤔 Memproses..."
												: isTTSGenerating
												? "💭 Memikirkan Respons..."
												: isTestScriptMode
												? "📝 Mode Evaluasi Test Script"
												: "👂 Siap Mendengarkan"
										}}
									</h2>
									<p class="text-base lg:text-lg opacity-75">
										{{
											isTestScriptMode
												? "Jawab pertanyaan untuk memberikan feedback"
												: isFluidMode
												? "Berbicara otomatis - tidak perlu klik tombol!"
												: "Tekan tombol mikrofon untuk mulai berbicara"
										}}
									</p>
								</div>

								<!-- Voice Controls -->
								<div
									class="flex items-center justify-center space-x-4 px-4"
									v-if="!isFluidMode || isTestScriptMode"
								>
									<button
										@click="startVoiceInput(true)"
										:disabled="
											isListening || isProcessingVoice || isTTSGenerating
										"
										:class="[
											'flex items-center space-x-2 px-4 lg:px-6 py-2 lg:py-3 rounded-full font-semibold transition-all text-sm lg:text-base',
											isListening
												? 'bg-red-500 text-white cursor-not-allowed'
												: 'bg-green-500 text-white hover:bg-green-600 hover:shadow-lg',
											(isProcessingVoice || isTTSGenerating) &&
												'opacity-50 cursor-not-allowed',
										]"
									>
										<Mic class="w-4 h-4 lg:w-5 lg:h-5" />
										<span class="hidden sm:inline">{{
											isListening
												? "Mendengarkan..."
												: isTestScriptMode
												? "Jawab Pertanyaan"
												: "Tekan untuk Bicara"
										}}</span>
										<span class="sm:hidden">{{
											isListening ? "🎙️" : "🗣️"
										}}</span>
									</button>

									<button
										v-if="isListening"
										@click="stopListening"
										class="flex items-center space-x-2 px-4 lg:px-6 py-2 lg:py-3 bg-red-500 text-white rounded-full font-semibold hover:bg-red-600 transition-all text-sm lg:text-base"
									>
										<MicOff class="w-4 h-4 lg:w-5 lg:h-5" />
										<span>Stop</span>
									</button>
								</div>

								<!-- Fluid Mode Status -->
								<div v-else class="text-center">
									<div
										class="bg-black bg-opacity-30 rounded-xl p-4 border border-green-500 border-opacity-30"
									>
										<div
											class="flex items-center justify-center space-x-2 text-green-300 mb-2"
										>
											<Zap class="w-5 h-5" />
											<span class="font-medium">Mode Fluid Aktif</span>
										</div>
										<p class="text-sm text-green-200 mb-3">
											{{
												isListening
													? "Sedang mendengarkan..."
													: "Berbicara otomatis - tidak perlu klik tombol!"
											}}
										</p>
										<div
											v-if="isListening"
											class="flex justify-center space-x-1"
										>
											<div
												class="w-2 h-2 bg-green-400 rounded-full animate-bounce"
											></div>
											<div
												class="w-2 h-2 bg-green-400 rounded-full animate-bounce"
												style="animation-delay: 0.1s"
											></div>
											<div
												class="w-2 h-2 bg-green-400 rounded-full animate-bounce"
												style="animation-delay: 0.2s"
											></div>
										</div>
									</div>
								</div>

								<!-- Conversation History Preview -->
								<div
									v-if="voiceMessages.length > 0"
									class="mt-6 lg:mt-8 w-full max-w-sm lg:max-w-2xl px-4"
								>
									<div class="bg-black bg-opacity-30 rounded-xl p-3 lg:p-4">
										<h3
											class="text-white font-semibold mb-2 lg:mb-3 text-center text-sm lg:text-base"
										>
											Percakapan Terakhir
										</h3>
										<div class="space-y-2 max-h-24 lg:max-h-32 overflow-y-auto">
											<div
												v-for="(message, index) in voiceMessages.slice(-3)"
												:key="index"
												:class="[
													'text-xs lg:text-sm p-2 rounded-lg',
													message.sender === 'user'
														? 'bg-green-500 bg-opacity-30 text-white ml-4 lg:ml-8'
														: 'bg-blue-500 bg-opacity-30 text-white mr-4 lg:mr-8',
												]"
											>
												<span class="font-medium"
													>{{
														message.sender === "user" ? "Anda" : "Ringan AI"
													}}:</span
												>
												{{ message.text }}
											</div>
										</div>
									</div>
								</div>
							</div>

							<!-- Fullscreen Mode Footer -->
							<div class="bg-black bg-opacity-20 p-3 lg:p-4 flex-shrink-0">
								<div
									class="flex items-center justify-between text-white text-xs lg:text-sm"
								>
									<div class="flex items-center space-x-2 lg:space-x-4">
										<span>💬 {{ voiceMessages.length }}</span>
										<span
											>⏱️
											{{
												formatDuration(
													Math.floor(
														(Date.now() - (speechStartTime || Date.now())) /
															1000
													)
												)
											}}</span
										>
									</div>
									<button
										@click="toggleTranscriptView"
										class="flex items-center space-x-1 hover:opacity-75"
									>
										<Eye class="w-3 h-3 lg:w-4 lg:h-4" />
										<span class="hidden sm:inline">Preview Transkrip</span>
										<span class="sm:hidden">📝</span>
									</button>
								</div>
							</div>
						</div>

						<!-- ConvAI Widget Interface -->
						<div
							v-else-if="activeMode === 'convai'"
							class="bg-white rounded-2xl shadow-soft overflow-hidden"
						>
							<!-- ConvAI Header -->
							<div
								class="bg-gradient-to-r from-orange-600 to-red-600 p-4 text-white"
							>
								<div class="flex items-center justify-between">
									<div class="flex items-center">
										<div
											class="w-10 h-10 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-3"
										>
											<Zap class="w-5 h-5 text-white" />
										</div>
										<div>
											<h3 class="font-semibold">Ringan AI - ConvAI Widget</h3>
											<div class="flex items-center text-sm opacity-90">
												<div
													class="w-2 h-2 bg-green-400 rounded-full mr-2"
												></div>
												Powered by ElevenLabs - {{ userName }}
											</div>
										</div>
									</div>
									<button
										@click="resetDemo"
										class="text-white opacity-75 hover:opacity-100 text-sm"
									>
										Reset Demo
									</button>
								</div>
							</div>

							<!-- ConvAI Widget Container -->
							<div class="p-4">
								<div class="bg-gray-50 rounded-xl p-4 mb-4">
									<div
										class="flex items-center space-x-2 text-sm text-gray-600 mb-2"
									>
										<Zap class="w-4 h-4 text-orange-500" />
										<span class="font-medium">ElevenLabs ConvAI</span>
									</div>
									<p class="text-sm text-gray-700">
										Widget percakapan AI yang canggih dengan teknologi
										speech-to-speech real-time dari ElevenLabs. Klik tombol di
										bawah untuk memulai percakapan interaktif!
									</p>
								</div>

								<!-- ElevenLabs ConvAI Widget -->
								<ElevenLabsConvAI
									agent-id="agent_01jwfpv8y9e3ssvr5qh5r8rwzv"
									class="rounded-lg overflow-hidden border border-gray-200"
								/>

								<div
									class="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200"
								>
									<div class="flex items-start space-x-2">
										<div
											class="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
										>
											<span class="text-white text-xs font-bold">i</span>
										</div>
										<div class="text-sm">
											<p class="font-medium text-blue-800 mb-1">
												Tips Penggunaan:
											</p>
											<ul class="text-blue-700 space-y-1">
												<li>
													• Klik tombol mikrofon di widget untuk memulai bicara
												</li>
												<li>
													• AI akan merespons dengan suara secara real-time
												</li>
												<li>• Pastikan mikrofon browser diizinkan</li>
												<li>• Gunakan headphone untuk pengalaman terbaik</li>
											</ul>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Sidebar -->
					<div class="space-y-6">
						<!-- User Info -->
						<div class="bg-white rounded-2xl p-6 shadow-soft">
							<h3 class="font-bold text-gray-900 mb-4 flex items-center">
								<User class="w-5 h-5 mr-2 text-purple-600" />
								Hai, {{ userName }}!
							</h3>
							<p class="text-sm text-gray-600">
								Senang bisa ngobrol denganmu. Cerita aja perasaanmu hari ini 💙
							</p>
						</div>

						<!-- Mood Selection -->
						<div class="bg-white rounded-2xl p-6 shadow-soft">
							<h3 class="font-bold text-gray-900 mb-4 flex items-center">
								<Smile class="w-5 h-5 mr-2 text-purple-600" />
								Bagaimana perasaanmu hari ini?
							</h3>
							<div class="grid grid-cols-2 gap-3">
								<button
									v-for="mood in moods"
									:key="mood.name"
									@click="selectMood(mood)"
									:disabled="isChatLimitReached"
									:class="[
										'p-3 rounded-xl border-2 transition-all text-center',
										selectedMood?.name === mood.name
											? 'border-purple-500 bg-purple-50'
											: 'border-gray-200 hover:border-purple-300',
										isChatLimitReached
											? 'opacity-50 cursor-not-allowed'
											: 'cursor-pointer',
									]"
								>
									<div class="text-2xl mb-1">{{ mood.emoji }}</div>
									<div class="text-xs font-medium text-gray-700">
										{{ mood.name }}
									</div>
								</button>
							</div>

							<div v-if="isChatLimitReached" class="mt-3 text-center">
								<p class="text-xs text-gray-500">Demo telah selesai</p>
							</div>
						</div>

						<!-- Demo Stats -->
						<div class="bg-white rounded-2xl p-6 shadow-soft">
							<h3 class="font-bold text-gray-900 mb-4 flex items-center">
								<TrendingUp class="w-5 h-5 mr-2 text-green-600" />
								Demo Progress
							</h3>
							<div class="space-y-3">
								<div class="flex justify-between items-center">
									<span class="text-sm text-gray-600">Pesan terkirim</span>
									<span class="font-semibold text-gray-900">{{
										ollamaMessages.filter((m) => m.sender === "user").length
									}}</span>
								</div>
								<div class="flex justify-between items-center">
									<span class="text-sm text-gray-600">Respon AI</span>
									<span class="font-semibold text-gray-900">{{
										ollamaMessages.filter((m) => m.sender === "ai").length
									}}</span>
								</div>
								<div class="flex justify-between items-center">
									<span class="text-sm text-gray-600">Percakapan tersisa</span>
									<span
										:class="[
											'font-semibold',
											isChatLimitReached ? 'text-red-600' : 'text-green-600',
										]"
									>
										{{ Math.max(0, maxChats - chatCount) }}
									</span>
								</div>
								<div class="flex justify-between items-center">
									<span class="text-sm text-gray-600">Mood dipilih</span>
									<span class="font-semibold text-gray-900">{{
										selectedMood ? "✓" : "✗"
									}}</span>
								</div>

								<!-- Voice Stats -->
								<div
									v-if="activeMode === 'voice'"
									class="pt-3 border-t border-gray-200"
								>
									<div class="flex justify-between items-center">
										<span class="text-sm text-gray-600">Mode suara</span>
										<span class="font-semibold text-gray-900">{{
											isFluidMode ? "Fluid" : "Manual"
										}}</span>
									</div>
									<div
										v-if="isFluidMode"
										class="flex justify-between items-center"
									>
										<span class="text-sm text-gray-600">Percakapan suara</span>
										<span class="font-semibold text-green-600"
											>{{ conversationCount }}/{{ maxFluidConversations }}</span
										>
									</div>
									<div class="flex justify-between items-center">
										<span class="text-sm text-gray-600">Status audio</span>
										<span
											:class="[
												'font-semibold text-xs px-2 py-1 rounded-full',
												isMuted
													? 'bg-red-100 text-red-600'
													: 'bg-green-100 text-green-600',
											]"
										>
											{{ isMuted ? "Muted" : "Active" }}
										</span>
									</div>
									<div
										v-if="isTestScriptMode"
										class="flex justify-between items-center"
									>
										<span class="text-sm text-gray-600">Test Script</span>
										<span class="font-semibold text-yellow-600">Aktif</span>
									</div>
								</div>
							</div>

							<!-- Progress Bar -->
							<div class="mt-4">
								<div class="flex justify-between text-xs text-gray-500 mb-1">
									<span>Progress Demo</span>
									<span>{{ chatCount }}/{{ maxChats }}</span>
								</div>
								<div class="w-full bg-gray-200 rounded-full h-2">
									<div
										class="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full transition-all duration-300"
										:style="{
											width: `${Math.min(100, (chatCount / maxChats) * 100)}%`,
										}"
									></div>
								</div>
							</div>
						</div>

						<!-- CTA -->
						<div
							class="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-6 text-white text-center"
						>
							<h3 class="font-bold mb-2">Suka dengan demo ini?</h3>
							<p class="text-sm text-purple-100 mb-4">
								Dapatkan akses penuh ke Ringan AI
							</p>
							<button
								class="w-full bg-white text-purple-600 font-semibold py-2 rounded-lg hover:bg-gray-100 transition-colors"
							>
								Download Aplikasi
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Transcript View Modal -->
		<div
			v-if="showTranscriptView"
			class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
		>
			<div
				class="bg-white rounded-2xl w-full max-w-sm sm:max-w-lg lg:max-w-2xl max-h-[85vh] sm:max-h-[80vh] overflow-hidden"
			>
				<div class="flex items-center justify-between p-3 sm:p-4 border-b">
					<h3 class="text-base sm:text-lg font-bold text-gray-900">
						Transkrip Percakapan Suara
					</h3>
					<button
						@click="showTranscriptView = false"
						class="p-1 hover:bg-gray-100 rounded"
					>
						<X class="w-4 h-4 sm:w-5 sm:h-5 text-gray-500" />
					</button>
				</div>

				<div class="p-3 sm:p-4 overflow-y-auto max-h-80 sm:max-h-96">
					<div
						v-if="conversationTranscript.length === 0"
						class="text-center py-6 sm:py-8 text-gray-500"
					>
						<p class="text-sm sm:text-base">
							Belum ada transkrip percakapan suara
						</p>
					</div>
					<div v-else class="space-y-3 sm:space-y-4">
						<!-- Session Info -->
						<div
							class="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-3 border border-green-200"
						>
							<div class="flex items-center justify-between text-sm">
								<div class="flex items-center space-x-2">
									<Volume2 class="w-4 h-4 text-green-600" />
									<span class="font-medium text-green-800"
										>Sesi Percakapan Suara</span
									>
								</div>
								<div class="text-green-700">
									{{ userName }} • {{ formatDuration(speechDuration) }}
								</div>
							</div>
							<p class="text-xs text-green-600 mt-1">
								{{ conversationTranscript.length }} pesan • Mode
								{{
									isTestScriptMode
										? "Test Script"
										: isFluidMode
										? "Fluid"
										: "Manual"
								}}
							</p>
						</div>

						<div
							v-for="(message, index) in conversationTranscript"
							:key="index"
							:class="[
								'flex',
								message.sender === 'user' ? 'justify-end' : 'justify-start',
							]"
						>
							<!-- AI Voice Message -->
							<div
								v-if="message.sender === 'ai'"
								class="flex items-start space-x-2 sm:space-x-3 max-w-xs sm:max-w-sm lg:max-w-md"
							>
								<div
									class="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center flex-shrink-0"
								>
									<Bot class="w-3 h-3 sm:w-4 sm:h-4 text-white" />
								</div>
								<div
									class="bg-green-50 rounded-2xl rounded-tl-none px-3 sm:px-4 py-2 sm:py-3 border border-green-200"
								>
									<p class="text-xs sm:text-sm text-gray-900">
										{{ message.text }}
									</p>
									<p class="text-xs text-gray-500 mt-1">{{ message.time }}</p>
								</div>
							</div>

							<!-- User Voice Message -->
							<div v-else class="max-w-xs sm:max-w-sm lg:max-w-md">
								<div
									class="bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-2xl rounded-br-none px-3 sm:px-4 py-2 sm:py-3"
								>
									<p class="text-xs sm:text-sm">{{ message.text }}</p>
									<p class="text-xs text-green-100 mt-1">{{ message.time }}</p>
								</div>
							</div>
						</div>
					</div>
				</div>

				<div
					class="border-t p-3 sm:p-4 flex flex-col sm:flex-row justify-between space-y-2 sm:space-y-0 sm:space-x-2"
				>
					<button
						@click="exportTranscript"
						class="px-3 sm:px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-xs sm:text-sm flex items-center justify-center space-x-2"
					>
						<span>📤</span>
						<span>Export Transkrip</span>
					</button>
					<button
						@click="copyTranscriptToChat"
						class="px-3 sm:px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-xs sm:text-sm flex items-center justify-center space-x-2"
					>
						<span>💬</span>
						<span>Copy ke Chat</span>
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch } from "vue";
import {
	Heart,
	ArrowLeft,
	Bot,
	User,
	Send,
	Smile,
	TrendingUp,
	Mic,
	MicOff,
	Volume2,
	MessageSquare,
	Zap,
	VolumeX,
	X,
	Eye,
} from "lucide-vue-next";

// Layout
definePageMeta({
	layout: false,
});

// Meta tags
useSeoMeta({
	title: "Demo Interaktif - Ringan AI Mental Health Assistant",
	description:
		"Coba langsung bagaimana rasanya berbicara dengan AI assistant Ringan yang peduli kesehatan mentalmu",
});

// Enhanced Ollama Chat integration with semantic search
const {
	sendMessage,
	sendMessageStream,
	isProcessing,
	isStreaming,
	error,
	isConnected,
	sessionId,
	messages: ollamaMessages,
	addMessage,
	clearMessages,
	hasMessages,
	lastMessage,
	isAssessmentActive,
	assessmentProgressPercentage,
	searchMentalHealthContext,
	getProblemCategories,
	getAssessmentQuestions,
	getTherapeuticSuggestions,
	startAssessment,
	continueAssessment,
	connectWebSocket,
} = useOllamaChat();

// Voice conversation integration (keeping for voice features)
const {
	isVoiceConversationActive,
	isProcessingVoice,
	voiceMessages,
	isSpeechSupported,
	isListening,
	isTTSGenerating,
	speechError,
	isFluidMode,
	isMuted,
	isTestScriptMode,
	testScriptMessages,
	conversationCount,
	maxFluidConversations,
	startVoiceConversation,
	stopVoiceConversation,
	startVoiceInput,
	stopListening,
	toggleFluidMode,
	toggleMute,
} = useVoiceConversation();

// Runtime config for demo limits
const config = useRuntimeConfig();
const maxChats = config.public.demoMaxChats;

// Reactive data
const currentInput = ref("");
const selectedMood = ref(null);
const showQuickResponses = ref(false);
const chatContainer = ref(null);
const voiceChatContainer = ref(null);
const userName = ref("");
const nameInput = ref("");
const chatCount = ref(0);
const showRegistrationCTA = ref(false);
const activeMode = ref("stream"); // 'text', 'voice', 'stream', or 'convai'

// Streaming chat data
const streamMessages = ref([]);
const streamInput = ref("");
const streamChatContainer = ref(null);
const streamError = ref(null);

// Add new reactive variables for fullscreen mode and transcript
const isFullscreenVoiceMode = ref(false);
const showTranscriptView = ref(false);
const conversationTranscript = ref([]);
const speechDuration = ref(0);
const speechStartTime = ref(null);

// Check if chat limit is reached
const isChatLimitReached = computed(() => {
	return chatCount.value >= maxChats;
});

// Moods data
const moods = ref([
	{ name: "Senang", emoji: "😊" },
	{ name: "Sedih", emoji: "😢" },
	{ name: "Cemas", emoji: "😰" },
	{ name: "Marah", emoji: "😠" },
	{ name: "Lelah", emoji: "😴" },
	{ name: "Bingung", emoji: "😕" },
]);

// Quick responses
const quickResponses = ref([
	"Aku merasa cemas",
	"Sedang stress",
	"Butuh motivasi",
	"Ingin curhat",
]);

// Get current time
const getCurrentTime = () => {
	return new Date().toLocaleTimeString("id-ID", {
		hour: "2-digit",
		minute: "2-digit",
	});
};

// Add message to chat (using composable's addMessage)
const addLocalMessage = (text, sender) => {
	addMessage({
		id: Date.now() + Math.random(),
		text,
		sender,
		time: getCurrentTime(),
	});
	scrollToBottom();
};

// Scroll to bottom of chat
const scrollToBottom = () => {
	nextTick(() => {
		if (chatContainer.value) {
			chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
		}
	});
};

// Scroll to bottom of voice chat
const scrollToBottomVoice = () => {
	nextTick(() => {
		if (voiceChatContainer.value) {
			voiceChatContainer.value.scrollTop =
				voiceChatContainer.value.scrollHeight;
		}
	});
};

// Start chat after name input
const startChat = () => {
	if (!nameInput.value.trim()) return;

	userName.value = nameInput.value.trim();

	// Ensure WebSocket connection is established
	const clientId = `demo_${userName.value}_${Date.now()}_${Math.random()
		.toString(36)
		.substr(2, 9)}`;
	connectWebSocket(clientId);

	// Welcome message
	setTimeout(() => {
		addLocalMessage(
			`Halo ${userName.value}! Aku Ringan AI, teman digitalmu untuk kesehatan mental. Senang sekali bisa kenal sama kamu! Bagaimana kabarmu hari ini? 😊`,
			"ai"
		);
		showQuickResponses.value = true;
	}, 500);
};

// Reset demo
const resetDemo = () => {
	userName.value = "";
	nameInput.value = "";
	clearMessages(); // Use composable's clearMessages
	selectedMood.value = null;
	showQuickResponses.value = false;
	currentInput.value = "";
	chatCount.value = 0;
	showRegistrationCTA.value = false;
	activeMode.value = "stream";

	// Reset streaming chat
	streamMessages.value = [];
	streamInput.value = "";

	// Clear stream errors
	streamError.value = null;

	// Reset voice conversation
	if (isVoiceConversationActive.value) {
		stopVoiceConversation();
	}
};

// Send message
const sendLocalMessage = async () => {
	if (
		!currentInput.value.trim() ||
		isProcessing.value ||
		isChatLimitReached.value
	)
		return;

	const userMessage = currentInput.value.trim();
	addLocalMessage(userMessage, "user");
	currentInput.value = "";
	showQuickResponses.value = false;

	// Increment chat count
	chatCount.value++;

	try {
		// Use WebSocket streaming chat with semantic search
		const response = await sendMessageStream(
			userMessage,
			{
				userName: userName.value,
				mode: "demo",
				chatCount: chatCount.value,
			},
			(chunk) => {
				// Handle streaming chunks - update the last AI message in real-time
				console.log("Streaming chunk:", chunk);
			}
		);

		if (response) {
			addLocalMessage(response.message, "ai");
		} else if (error.value) {
			addLocalMessage(
				"Maaf, terjadi kesalahan. Silakan coba lagi nanti.",
				"ai"
			);
		}
	} catch (err) {
		addLocalMessage("Maaf, terjadi kesalahan. Silakan coba lagi nanti.", "ai");
	} finally {
		// Check if chat limit is reached
		if (isChatLimitReached.value) {
			showRegistrationCTA.value = true;
			showQuickResponses.value = false;

			// Show limit reached message
			setTimeout(() => {
				addLocalMessage(
					`Wah, kamu sudah mencoba ${maxChats} percakapan! 🎉 Untuk melanjutkan ngobrol tanpa batas, yuk daftar di aplikasi Ringan. Kamu akan mendapatkan akses penuh ke semua fitur! 💙`,
					"ai"
				);
			}, 1000);
		} else {
			showQuickResponses.value = true;
		}
	}
};

// Send quick response
const sendQuickResponse = (response) => {
	if (isChatLimitReached.value) return;
	currentInput.value = response;
	sendLocalMessage();
};

// Select mood
const selectMood = async (mood) => {
	if (isChatLimitReached.value) return;

	selectedMood.value = mood;

	// Send mood as message
	const moodMessage = `Aku merasa ${mood.name.toLowerCase()} hari ini ${
		mood.emoji
	}`;
	addLocalMessage(moodMessage, "user");

	// Increment chat count
	chatCount.value++;

	try {
		// Use WebSocket streaming chat with semantic search
		const response = await sendMessageStream(
			moodMessage,
			{
				userName: userName.value,
				mode: "demo",
				mood: mood.name,
				chatCount: chatCount.value,
			},
			(chunk) => {
				// Handle streaming chunks - update the last AI message in real-time
				console.log("Streaming chunk:", chunk);
			}
		);

		if (response) {
			addLocalMessage(response.message, "ai");
		} else if (error.value) {
			addLocalMessage(
				"Maaf, terjadi kesalahan. Silakan coba lagi nanti.",
				"ai"
			);
		}
	} catch (err) {
		addLocalMessage("Maaf, terjadi kesalahan. Silakan coba lagi nanti.", "ai");
	} finally {
		// Check if chat limit is reached
		if (isChatLimitReached.value) {
			showRegistrationCTA.value = true;
			showQuickResponses.value = false;

			// Show limit reached message
			setTimeout(() => {
				addLocalMessage(
					`Wah, kamu sudah mencoba ${maxChats} percakapan! 🎉 Untuk melanjutkan ngobrol tanpa batas, yuk daftar di aplikasi Ringan. Kamu akan mendapatkan akses penuh ke semua fitur! 💙`,
					"ai"
				);
			}, 1000);
		} else {
			showQuickResponses.value = true;
		}
	}
};

// Streaming chat functions
const addStreamMessage = (text, sender) => {
	const message = {
		id: Date.now() + Math.random(),
		text,
		sender,
		time: new Date().toLocaleTimeString("id-ID", {
			hour: "2-digit",
			minute: "2-digit",
		}),
	};
	streamMessages.value.push(message);

	// Auto scroll to bottom
	nextTick(() => {
		if (streamChatContainer.value) {
			streamChatContainer.value.scrollTop =
				streamChatContainer.value.scrollHeight;
		}
	});
};

const sendStreamMessage = async () => {
	if (!streamInput.value.trim() || isStreaming.value) return;

	const userMessage = streamInput.value.trim();
	addStreamMessage(userMessage, "user");
	streamInput.value = "";

	try {
		// Use enhanced Ollama streaming chat with semantic search
		const response = await sendMessageStream(
			userMessage,
			{
				userName: userName.value,
				mode: "demo",
				chatCount: chatCount.value,
			},
			(chunk) => {
				// Handle streaming chunks if needed
				console.log("Streaming chunk:", chunk);
			}
		);

		if (response) {
			addStreamMessage(response.message, "ai");
		} else if (error.value) {
			addStreamMessage(
				"Maaf, terjadi kesalahan. Silakan coba lagi nanti.",
				"ai"
			);
		}
	} catch (err) {
		console.error("Stream message error:", err);
		addStreamMessage("Maaf, terjadi kesalahan. Silakan coba lagi nanti.", "ai");
	}
};

const clearStreamError = () => {
	// Clear the local stream error
	streamError.value = null;
};

// Watch for stream messages changes to auto-scroll
watch(
	streamMessages,
	() => {
		nextTick(() => {
			if (streamChatContainer.value) {
				streamChatContainer.value.scrollTop =
					streamChatContainer.value.scrollHeight;
			}
		});
	},
	{ deep: true }
);

// Watch for voice messages changes to auto-scroll
watch(
	voiceMessages,
	() => {
		scrollToBottomVoice();
	},
	{ deep: true }
);

// Add new methods for fullscreen mode and transcript
const startFullscreenVoiceMode = () => {
	isFullscreenVoiceMode.value = true;
	speechStartTime.value = Date.now();
	startVoiceConversation();
};

const endFullscreenVoiceMode = () => {
	isFullscreenVoiceMode.value = false;

	// Calculate duration
	if (speechStartTime.value) {
		speechDuration.value = Math.floor(
			(Date.now() - speechStartTime.value) / 1000
		);
	}

	// Copy voice messages to transcript
	conversationTranscript.value = [...voiceMessages.value];

	// Stop voice conversation
	stopVoiceConversation();

	// Show transcript if there are messages
	if (conversationTranscript.value.length > 0) {
		setTimeout(() => {
			showTranscriptView.value = true;
		}, 500);
	}
};

const toggleTranscriptView = () => {
	showTranscriptView.value = !showTranscriptView.value;
};

const copyTranscriptToChat = () => {
	// Copy all transcript messages to the main chat
	conversationTranscript.value.forEach((message) => {
		addMessage(message.text, message.sender);
	});

	showTranscriptView.value = false;

	// Switch to stream mode to show the copied messages
	activeMode.value = "stream";
};

const exportTranscript = () => {
	const transcriptData = {
		timestamp: new Date().toISOString(),
		duration: speechDuration.value,
		messages: conversationTranscript.value,
		userName: userName.value,
	};

	const blob = new Blob([JSON.stringify(transcriptData, null, 2)], {
		type: "application/json",
	});
	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = `ringan-voice-conversation-${
		new Date().toISOString().split("T")[0]
	}.json`;
	a.click();
	URL.revokeObjectURL(url);
};

const formatDuration = (seconds) => {
	const minutes = Math.floor(seconds / 60);
	const remainingSeconds = seconds % 60;
	return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
};

// Initialize WebSocket connection on mount
onMounted(() => {
	// Connect WebSocket for streaming chat
	const clientId = `demo_${Date.now()}_${Math.random()
		.toString(36)
		.substr(2, 9)}`;
	connectWebSocket(clientId);
});
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
	box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1),
		0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.animate-fade-in {
	animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
	from {
		opacity: 0;
		transform: translateY(10px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}

/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
	width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
	background: #f1f5f9;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
	background: #cbd5e1;
	border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
	background: #94a3b8;
}
</style>
