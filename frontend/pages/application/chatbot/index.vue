<template>
	<div class="flex flex-col h-screen overflow-hidden">
		<!-- Header -->
		<div
			class="bg-white border-b border-gray-200 p-2 sm:p-3 lg:p-4 flex-shrink-0 z-10"
		>
			<div class="flex items-center justify-between">
				<div class="flex items-center space-x-2 sm:space-x-3">
					<div
						class="w-7 h-7 sm:w-8 sm:h-8 lg:w-10 lg:h-10 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center"
					>
						<Bot class="w-3 h-3 sm:w-4 sm:h-4 lg:w-5 lg:h-5 text-white" />
					</div>
					<div class="min-w-0 flex-1">
						<h1
							class="font-bold text-gray-900 text-xs sm:text-sm lg:text-base truncate"
						>
							{{ t('header.aiCounselor') }}
						</h1>
						<p class="text-xs text-gray-500 hidden xs:block truncate">
								{{ ollamaIsProcessing ? t('header.typing') : t('header.ready') }}
							</p>
					</div>
				</div>

				<div
					class="flex items-center space-x-1 sm:space-x-2 relative flex-shrink-0"
					ref="menuContainer"
				>
					<!-- Speech Mode Toggle -->
					<button
						@click="toggleSpeechMode"
						:class="[
							'flex items-center space-x-1 px-2 py-1.5 sm:px-3 sm:py-2 rounded-lg text-xs font-medium transition-all min-w-0',
							isSpeechMode
								? 'bg-green-500 text-white'
								: 'bg-gray-100 text-gray-600 hover:bg-gray-200',
						]"
					>
						<Volume2 class="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" />
						<span class="hidden xs:inline truncate">{{
							isSpeechMode ? t('header.speechOn') : t('header.speech')
						}}</span>
						<span class="xs:hidden">🎙️</span>
					</button>

					<!-- Intent Mode Selector -->
					<select
						v-model="currentMode"
						@change="handleModeChange"
						class="text-xs bg-gray-100 border-0 rounded-lg px-1.5 sm:px-2 py-1.5 sm:py-2 focus:ring-2 focus:ring-blue-500 min-w-0 max-w-16 sm:max-w-20 lg:max-w-none"
					>
						<option value="help">
							{{ isMobile ? t('header.help') : t('header.modeHelp') }}
						</option>
						<option value="tips">
							{{ isMobile ? t('header.tips') : t('header.dailyTips') }}
						</option>
						<option value="chat">
							{{ isMobile ? t('header.chat') : t('header.freeChat') }}
						</option>
					</select>

					<!-- Language Switcher -->
					<button
						@click="switchLanguage"
						:title="t('language.switch')"
						class="flex items-center space-x-1 px-2 py-1.5 sm:px-3 sm:py-2 rounded-lg text-xs font-medium transition-all min-w-0 bg-gray-100 text-gray-600 hover:bg-gray-200"
					>
						<Globe class="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" />
						<span class="hidden xs:inline truncate">{{ locale === 'id' ? 'EN' : 'ID' }}</span>
					</button>

					<!-- Menu Button -->
					<button
						@click="showMenu = !showMenu"
						class="p-1.5 sm:p-2 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors flex-shrink-0"
					>
						<MoreVertical class="w-3 h-3 sm:w-4 sm:h-4" />
					</button>

					<!-- Menu Dropdown -->
					<div
						v-if="showMenu"
						class="absolute right-0 top-full mt-2 w-40 sm:w-44 lg:w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-50"
					>
						<button
							@click="
								clearHistory();
								showMenu = false;
							"
							class="w-full text-left px-3 py-2.5 sm:py-3 text-xs sm:text-sm text-gray-700 hover:bg-gray-100 rounded-t-lg"
						>
							{{ t('menu.clearHistory') }}
						</button>
						<button
							@click="
								exportChat();
								showMenu = false;
							"
							class="w-full text-left px-3 py-2.5 sm:py-3 text-xs sm:text-sm text-gray-700 hover:bg-gray-100"
						>
							{{ t('menu.exportChat') }}
						</button>
						<button
							@click="
								toggleTranscriptView();
								showMenu = false;
							"
							v-if="conversationTranscript.length > 0"
							class="w-full text-left px-3 py-2.5 sm:py-3 text-xs sm:text-sm text-gray-700 hover:bg-gray-100"
						>
							{{ t('menu.viewTranscript') }}
						</button>
						<button
							@click="
								showPrivacySettings = true;
								showMenu = false;
							"
							class="w-full text-left px-3 py-2.5 sm:py-3 text-xs sm:text-sm text-gray-700 hover:bg-gray-100"
						>
							{{ t('menu.privacySettings') }}
						</button>
						<div class="border-t border-gray-200">
							<button
								@click="
									showEmergencyInfo = true;
									showMenu = false;
								"
								class="w-full text-left px-3 py-2.5 sm:py-3 text-xs sm:text-sm text-red-600 hover:bg-red-50 rounded-b-lg"
							>
								{{ t('menu.emergencyHelp') }}
							</button>
						</div>
					</div>
				</div>
			</div>

			<!-- Mode Description -->
			<div class="mt-2 text-xs text-gray-600 hidden sm:block">
				{{ getModeDescription(currentMode) }}
			</div>
		</div>

		<!-- Full Screen Speech Mode -->
		<div
			v-if="isSpeechMode"
			class="fixed inset-0 bg-gradient-to-br from-blue-900 via-purple-900 to-green-900 z-50 flex flex-col"
		>
			<!-- Speech Mode Header -->
			<div class="bg-black bg-opacity-20 p-2 sm:p-3 lg:p-4 flex-shrink-0">
				<div class="flex items-center justify-between">
					<div class="flex items-center space-x-2 sm:space-x-3 min-w-0 flex-1">
						<div
							class="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center flex-shrink-0"
						>
							<Volume2 class="w-4 h-4 sm:w-5 sm:h-5 lg:w-6 lg:h-6 text-white" />
						</div>
						<div class="text-white min-w-0 flex-1">
							<h1 class="font-bold text-sm sm:text-base lg:text-lg truncate">
								AI Voice Counselor
							</h1>
							<p class="text-xs sm:text-sm opacity-75 truncate">
								{{
									isFluidConversationActive.value
										? "Mode Otomatis Aktif"
										: "Mode Manual"
								}}
								{{ speechStatus }}
							</p>
						</div>
					</div>

					<div class="flex items-center space-x-1 sm:space-x-2 flex-shrink-0">
						<!-- Fluid Mode Toggle -->
						<button
							@click="toggleFluidConversation"
							:class="[
								'flex items-center space-x-1 px-2 py-1.5 sm:px-3 sm:py-2 rounded-lg text-xs font-medium transition-all min-w-0',
								isFluidConversationActive.value
									? 'bg-yellow-500 bg-opacity-30 text-yellow-200 border border-yellow-400'
									: 'bg-white bg-opacity-20 text-white border border-white border-opacity-30',
							]"
						>
							<Zap class="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" />
							<span class="hidden xs:inline truncate">{{
								isFluidConversationActive.value ? "Auto ON" : "Manual"
							}}</span>
							<span class="xs:hidden">{{
								isFluidConversationActive.value ? "⚡" : "📱"
							}}</span>
						</button>

						<!-- Close Speech Mode -->
						<button
							@click="endSpeechConversation"
							class="text-white opacity-75 hover:opacity-100 text-xs sm:text-sm flex items-center space-x-1 p-1.5 sm:p-2"
						>
							<X class="w-3 h-3 sm:w-4 sm:h-4" />
							<span class="hidden xs:inline">End</span>
						</button>
					</div>
				</div>

				<!-- Fluid Mode Progress -->
				<div v-if="isFluidConversationActive.value" class="mt-2 sm:mt-3">
					<div
						class="flex items-center justify-between text-xs sm:text-sm text-white"
					>
						<span class="truncate">Percakapan Otomatis</span>
						<span class="flex-shrink-0"
							>{{ fluidConversationCount }}/{{ maxFluidConversations }}</span
						>
					</div>
					<div class="mt-1 w-full bg-white bg-opacity-20 rounded-full h-1">
						<div
							class="bg-yellow-400 h-1 rounded-full transition-all duration-300"
							:style="{
								width: `${
									(fluidConversationCount / maxFluidConversations) * 100
								}%`,
							}"
						></div>
					</div>
				</div>
			</div>

			<!-- Main Speech Interface -->
			<div
				class="flex-1 flex flex-col items-center justify-center p-3 sm:p-4 lg:p-8"
			>
				<!-- Central Audio Visualizer -->
				<div class="mb-4 sm:mb-6 lg:mb-8">
					<div
						:class="[
							'w-20 h-20 sm:w-24 sm:h-24 lg:w-32 lg:h-32 rounded-full flex items-center justify-center transition-all duration-300',
							isListening
								? 'bg-red-500 bg-opacity-30 border-4 border-red-400 animate-pulse'
								: isProcessingSpeech
								? 'bg-blue-500 bg-opacity-30 border-4 border-blue-400 animate-bounce'
								: 'bg-white bg-opacity-20 border-4 border-white border-opacity-30',
						]"
					>
						<div
							:class="[
								'w-12 h-12 sm:w-16 sm:h-16 lg:w-20 lg:h-20 rounded-full flex items-center justify-center transition-all',
								isListening
									? 'bg-red-500'
									: isProcessingSpeech
									? 'bg-blue-500'
									: 'bg-green-500',
							]"
						>
							<Mic
								v-if="isListening"
								class="w-6 h-6 sm:w-8 sm:h-8 lg:w-10 lg:h-10 text-white"
							/>
							<Bot
								v-else-if="isProcessingSpeech"
								class="w-6 h-6 sm:w-8 sm:h-8 lg:w-10 lg:h-10 text-white"
							/>
							<Volume2
								v-else
								class="w-6 h-6 sm:w-8 sm:h-8 lg:w-10 lg:h-10 text-white"
							/>
						</div>
					</div>
				</div>

				<!-- Status Text -->
				<div class="text-center text-white mb-4 sm:mb-6 lg:mb-8 px-3 sm:px-4">
					<h2 class="text-base sm:text-lg lg:text-2xl font-bold mb-2">
					{{
						isListening
							? t('speechMode.listening')
							: isProcessingSpeech
							? t('speechMode.processing')
							: isGeneratingResponse
							? t('speechMode.thinking')
							: t('speechMode.ready')
					}}
				</h2>
					<p
					class="text-sm sm:text-base lg:text-lg opacity-75 max-w-xs sm:max-w-md lg:max-w-lg mx-auto"
				>
					{{
						currentSpeechText || t('speechMode.instruction')
					}}
				</p>
				</div>

				<!-- Voice Controls -->
				<div
					class="flex items-center justify-center space-x-3 sm:space-x-4 px-3 sm:px-4"
				>
					<button
						v-if="!isFluidConversationActive.value"
						@click="startVoiceInput"
						:disabled="
							isListening || isProcessingSpeech || isGeneratingResponse
						"
						:class="[
							'flex items-center space-x-2 px-3 sm:px-4 lg:px-6 py-2 sm:py-2.5 lg:py-3 rounded-full font-semibold transition-all text-sm sm:text-base min-w-0',
							isListening
								? 'bg-red-500 text-white cursor-not-allowed'
								: 'bg-green-500 text-white hover:bg-green-600 hover:shadow-lg',
							(isProcessingSpeech || isGeneratingResponse) &&
								'opacity-50 cursor-not-allowed',
						]"
					>
						<Mic class="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" />
						<span class="hidden xs:inline truncate">{{
						isListening ? t('speechMode.listeningButton') : t('speechMode.talkButton')
					}}</span>
					<span class="xs:hidden">{{
						isListening ? t('speechMode.listeningShort') : t('speechMode.talkShort')
					}}</span>
					</button>

					<button
						v-if="isListening"
						@click="stopVoiceInput"
						class="flex items-center space-x-2 px-3 sm:px-4 lg:px-6 py-2 sm:py-2.5 lg:py-3 bg-red-500 text-white rounded-full font-semibold hover:bg-red-600 transition-all text-sm sm:text-base"
					>
						<MicOff class="w-4 h-4 sm:w-5 sm:h-5" />
						<span>Stop</span>
					</button>
				</div>

				<!-- Conversation History Preview -->
				<div
					v-if="speechMessages.length > 0"
					class="mt-4 sm:mt-6 lg:mt-8 w-full max-w-xs sm:max-w-sm lg:max-w-2xl px-3 sm:px-4"
				>
					<div class="bg-black bg-opacity-30 rounded-xl p-2 sm:p-3 lg:p-4">
						<h3
							class="text-white font-semibold mb-2 sm:mb-2 lg:mb-3 text-center text-xs sm:text-sm lg:text-base"
						>
							Percakapan Terakhir
						</h3>
						<div
							class="space-y-1.5 sm:space-y-2 max-h-20 sm:max-h-24 lg:max-h-32 overflow-y-auto"
						>
							<div
								v-for="(message, index) in speechMessages.slice(-3)"
								:key="index"
								:class="[
									'text-xs sm:text-sm p-1.5 sm:p-2 rounded-lg',
									message.sender === 'user'
										? 'bg-green-500 bg-opacity-30 text-white ml-2 sm:ml-4 lg:ml-8'
										: 'bg-blue-500 bg-opacity-30 text-white mr-2 sm:mr-4 lg:mr-8',
								]"
							>
								<span class="font-medium"
									>{{ message.sender === "user" ? "Anda" : "AI" }}:</span
								>
								<span class="truncate block">{{ message.text }}</span>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Speech Mode Footer -->
			<div class="bg-black bg-opacity-20 p-2 sm:p-3 lg:p-4 flex-shrink-0">
				<div
					class="flex items-center justify-between text-white text-xs sm:text-sm"
				>
					<div class="flex items-center space-x-2 sm:space-x-4">
						<span>💬 {{ speechMessages.length }}</span>
						<span>⏱️ {{ formatDuration(speechDuration) }}</span>
					</div>
					<button
						@click="toggleTranscriptPreview"
						class="flex items-center space-x-1 hover:opacity-75 p-1"
					>
						<Eye class="w-3 h-3 sm:w-4 sm:h-4" />
						<span class="hidden xs:inline">{{ t('transcript.preview') }}</span>
						<span class="xs:hidden">📝</span>
					</button>
				</div>
			</div>
		</div>

		<!-- Transcript View Modal -->
		<div
			v-if="showTranscriptView"
			class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-2 sm:p-4"
		>
			<div
				class="bg-white rounded-2xl w-full max-w-xs sm:max-w-sm lg:max-w-lg xl:max-w-2xl max-h-[90vh] sm:max-h-[85vh] lg:max-h-[80vh] overflow-hidden"
			>
				<div class="flex items-center justify-between p-3 sm:p-4 border-b">
					<h3
						class="text-sm sm:text-base lg:text-lg font-bold text-gray-900 truncate"
					>
						{{ t('transcript.title') }}
					</h3>
					<button
						@click="showTranscriptView = false"
						class="p-1.5 sm:p-2 hover:bg-gray-100 rounded flex-shrink-0"
					>
						<X class="w-4 h-4 sm:w-5 sm:h-5 text-gray-500" />
					</button>
				</div>

				<div
					class="p-2 sm:p-3 lg:p-4 overflow-y-auto max-h-60 sm:max-h-80 lg:max-h-96"
				>
					<div
						v-if="conversationTranscript.length === 0"
						class="text-center py-4 sm:py-6 lg:py-8 text-gray-500"
					>
						<p class="text-xs sm:text-sm lg:text-base">
						{{ t('transcript.empty') }}
					</p>
					</div>
					<div v-else class="space-y-2 sm:space-y-3 lg:space-y-4">
						<div
							v-for="(message, index) in conversationTranscript"
							:key="index"
							:class="[
								'flex',
								message.sender === 'user' ? 'justify-end' : 'justify-start',
							]"
						>
							<div
								v-if="message.sender === 'ai'"
								class="flex items-start space-x-2 sm:space-x-3 max-w-[85%] sm:max-w-xs lg:max-w-sm xl:max-w-md"
							>
								<div
									class="w-5 h-5 sm:w-6 sm:h-6 lg:w-8 lg:h-8 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center flex-shrink-0"
								>
									<Bot
										class="w-2.5 h-2.5 sm:w-3 sm:h-3 lg:w-4 lg:h-4 text-white"
									/>
								</div>
								<div
									class="bg-gray-100 rounded-2xl rounded-tl-none px-2 sm:px-3 lg:px-4 py-1.5 sm:py-2 lg:py-3"
								>
									<p
										class="text-xs sm:text-sm lg:text-base text-gray-900 break-words"
									>
										{{ message.text }}
									</p>
									<p class="text-xs text-gray-500 mt-1">{{ message.time }}</p>
								</div>
							</div>

							<div
								v-else
								class="max-w-[85%] sm:max-w-xs lg:max-w-sm xl:max-w-md"
							>
								<div
									class="bg-green-600 text-white rounded-2xl rounded-br-none px-2 sm:px-3 lg:px-4 py-1.5 sm:py-2 lg:py-3"
								>
									<p class="text-xs sm:text-sm lg:text-base break-words">
										{{ message.text }}
									</p>
									<p class="text-xs text-green-100 mt-1">{{ message.time }}</p>
								</div>
							</div>
						</div>
					</div>
				</div>

				<div
					class="border-t p-2 sm:p-3 lg:p-4 flex flex-col sm:flex-row justify-between space-y-2 sm:space-y-0 sm:space-x-2"
				>
					<button
						@click="exportTranscript"
						class="px-2 sm:px-3 lg:px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-xs sm:text-sm flex-1 sm:flex-none"
					>
						{{ t('transcript.export') }}
				</button>
				<button
					@click="copyTranscriptToChat"
					class="px-2 sm:px-3 lg:px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-xs sm:text-sm flex-1 sm:flex-none"
				>
					{{ t('transcript.copyToChat') }}
					</button>
				</div>
			</div>
		</div>

		<!-- Messages Container -->
		<div
			ref="messagesContainer"
			class="overflow-y-auto p-2 sm:p-3 lg:p-4 space-y-1 sm:space-y-2 lg:space-y-4 bg-gray-50 h-[calc(100vh-200px)] sm:h-[calc(100vh-200px)] lg:h-[calc(100vh-220px)] pb-32 sm:pb-32 lg:pb-36"
		>
			<!-- Welcome Message -->
			<div
				v-if="ollamaMessages.length === 0"
				class="text-center py-6 sm:py-8 lg:py-12"
			>
				<div
					class="w-16 h-16 sm:w-20 sm:h-20 lg:w-24 lg:h-24 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4 sm:mb-6 shadow-lg"
				>
					<Heart class="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 text-white" />
				</div>
				<h3
					class="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900 mb-3 sm:mb-4"
				>
					{{ t('welcome.greeting') }}
				</h3>
				<p
					class="text-gray-600 text-sm sm:text-base lg:text-lg mb-6 sm:mb-8 px-4 sm:px-6 max-w-sm sm:max-w-md mx-auto leading-relaxed"
				>
					{{ t('welcome.description') }}
				</p>

				<!-- Quick Intent Buttons -->
				<div
					class="grid grid-cols-1 gap-3 max-w-sm sm:max-w-md mx-auto px-4 sm:px-6"
				>
					<button
						v-for="intent in quickIntents"
						:key="intent.id"
						@click="sendQuickMessage(intent.message, intent.mode)"
						class="p-4 bg-white rounded-2xl border border-gray-200 text-sm sm:text-base text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 text-left shadow-sm hover:shadow-md"
					>
						<div class="flex items-center space-x-3">
							<span class="text-xl sm:text-2xl flex-shrink-0">{{
								intent.emoji
							}}</span>
							<span class="font-medium">{{ intent.label }}</span>
						</div>
					</button>
				</div>
			</div>

			<!-- Messages -->
			<div
				v-for="message in ollamaMessages"
				:key="message.id"
				:class="[
					'flex mb-1 sm:mb-2',
					message.sender === 'user' ? 'justify-end' : 'justify-start',
				]"
			>
				<!-- AI Message -->
				<div
					v-if="message.sender === 'ai'"
					class="flex items-start space-x-2 sm:space-x-3 max-w-[88%] sm:max-w-xs lg:max-w-sm xl:max-w-md"
				>
					<div
						class="w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1"
					>
						<Bot class="w-3 h-3 sm:w-3.5 sm:h-3.5 lg:w-4 lg:h-4 text-white" />
					</div>
					<div
						class="bg-white rounded-3xl rounded-tl-md px-3 sm:px-4 lg:px-5 py-2 sm:py-2.5 lg:py-3 shadow-sm border border-gray-100"
					>
						<div
							v-html="message.text"
							class="text-sm sm:text-base lg:text-base text-gray-900 whitespace-pre-wrap prose prose-sm max-w-none break-words leading-relaxed"
						></div>

						<!-- Streaming Indicator -->
						<div
							v-if="message.isStreaming"
							class="flex items-center space-x-1 mt-2"
						>
							<div class="flex space-x-1">
								<div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
								<div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
								<div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
							</div>
							<span class="text-xs text-gray-500 ml-2">{{ t('status.typing') }}</span>
						</div>

						<!-- Assessment Transition Suggestion -->
						<div
							v-if="message.showAssessmentTransition && message.contextAnalysis"
							class="mt-3 p-3 sm:p-4 bg-blue-50 border border-blue-200 rounded-2xl"
						>
							<div class="flex items-start space-x-3">
								<div
									class="w-5 h-5 sm:w-6 sm:h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
								>
									<svg
										class="w-3 h-3 sm:w-3.5 sm:h-3.5 text-white"
										fill="currentColor"
										viewBox="0 0 20 20"
									>
										<path
											fill-rule="evenodd"
											d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
											clip-rule="evenodd"
										></path>
									</svg>
								</div>
								<div class="flex-1 min-w-0">
									<h4
										class="text-sm sm:text-base font-semibold text-blue-900 mb-2"
 									>
										{{ t('assessment.structuredAvailable.title') }}
									</h4>
									<p class="text-sm text-blue-700 mb-3 leading-relaxed">
										{{ t('assessment.structuredAvailable.description') }}
										<span v-if="message.contextAnalysis?.primary_category" class="font-medium">
											{{ message.contextAnalysis.primary_category }}
										</span>.
									</p>
									<div class="flex flex-col sm:flex-row gap-2">
										<button
												@click="acceptAssessment(message)"
												class="px-4 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-xl hover:bg-blue-700 transition-colors shadow-sm"
											>
												{{ t('assessment.structuredAvailable.startButton') }}
											</button>
											<button
												@click="declineAssessment(message)"
												class="px-4 py-2.5 bg-gray-100 text-gray-700 text-sm font-medium rounded-xl hover:bg-gray-200 transition-colors"
											>
												{{ t('assessment.structuredAvailable.continueButton') }}
											</button>
									</div>
								</div>
							</div>
						</div>

						<div
							v-if="message.detectedEmotion"
							class="mt-2 flex items-center space-x-1"
						>
							<span class="text-xs text-blue-600"
								>Detected: {{ message.detectedEmotion }}</span
							>
						</div>
						<p class="text-xs text-gray-400 mt-2">
							{{ formatTime(message.timestamp) }}
						</p>
					</div>
				</div>

				<!-- User Message -->
				<div v-else class="max-w-[88%] sm:max-w-xs lg:max-w-sm xl:max-w-md">
					<div
						class="bg-blue-500 text-white rounded-3xl rounded-br-md px-3 sm:px-4 lg:px-5 py-2 sm:py-2.5 lg:py-3 shadow-sm"
					>
						<p
							class="text-sm sm:text-base lg:text-base whitespace-pre-wrap break-words leading-relaxed"
						>
							{{ message.text }}
						</p>
						<div class="flex items-center justify-between mt-2">
							<p class="text-xs text-blue-100 opacity-75">
								{{ formatTime(message.timestamp) }}
							</p>
							<div
								v-if="message.emotionTone"
								class="flex items-center space-x-1"
							>
								<span class="text-sm">{{
									getEmotionEmoji(message.emotionTone)
								}}</span>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Crisis Alert -->
			<div
				v-if="showCrisisAlert"
				class="bg-red-50 border border-red-200 rounded-2xl p-4 sm:p-5 lg:p-6 mx-2 sm:mx-3"
			>
				<div class="flex items-start space-x-3 sm:space-x-4">
					<AlertTriangle
						class="w-5 h-5 sm:w-6 sm:h-6 text-red-600 mt-0.5 flex-shrink-0"
					/>
					<div class="min-w-0 flex-1">
						<h3
							class="font-semibold text-red-900 mb-3 text-sm sm:text-base lg:text-lg"
						>
							Perhatian: Bantuan Darurat
						</h3>
						<p class="text-sm sm:text-base text-red-700 mb-4 leading-relaxed">
							Saya mendeteksi Anda mungkin membutuhkan bantuan segera. Jangan
							ragu untuk menghubungi:
						</p>
						<div class="space-y-2 text-sm sm:text-base">
							<p class="text-red-800 font-medium">🏥 Emergency: 112</p>
							<p class="text-red-800 font-medium">
								💬 Crisis Hotline: 119 ext 8
							</p>
							<p class="text-red-800 font-medium">💚 Sejiwa: 119 ext 8</p>
						</div>
						<div class="flex flex-col sm:flex-row gap-3 mt-4">
							<button
								@click="callEmergency"
								class="px-4 py-3 bg-red-600 text-white text-sm font-medium rounded-xl hover:bg-red-700 transition-colors shadow-sm"
							>
								Hubungi Sekarang
							</button>
							<button
								@click="dismissCrisisAlert"
								class="px-4 py-3 border border-red-300 text-red-700 text-sm font-medium rounded-xl hover:bg-red-50 transition-colors"
							>
								Saya Baik-baik Saja
							</button>
						</div>
					</div>
				</div>
			</div>

			<!-- Assessment Interface -->
			<div
				v-if="isAssessmentActive"
				class="bg-blue-50 border border-blue-200 rounded-2xl p-4 sm:p-5 lg:p-6 mx-2 sm:mx-3 mb-4"
			>
				<div class="flex items-start space-x-3 sm:space-x-4">
					<div
						class="w-8 h-8 sm:w-10 sm:h-10 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0"
					>
						<svg
							class="w-4 h-4 sm:w-5 sm:h-5 text-white"
							fill="currentColor"
							viewBox="0 0 20 20"
						>
							<path
								fill-rule="evenodd"
								d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
								clip-rule="evenodd"
							></path>
						</svg>
					</div>
					<div class="min-w-0 flex-1">
						<h3
							class="font-semibold text-blue-900 mb-3 text-sm sm:text-base lg:text-lg"
						>
							Assessment Terstruktur
						</h3>

						<!-- Progress Bar -->
						<div class="mb-4">
							<div class="flex justify-between text-xs sm:text-sm text-blue-700 mb-2">
								<span>Progress Assessment</span>
								<span>{{ Math.round(assessmentProgressPercentage) }}%</span>
							</div>
							<div class="w-full bg-blue-200 rounded-full h-2">
								<div
									class="bg-blue-600 h-2 rounded-full transition-all duration-300"
									:style="{ width: assessmentProgressPercentage + '%' }"
								></div>
							</div>
						</div>

						<!-- Current Assessment Question -->
						<div
							v-if="lastMessage && lastMessage.assessmentData && lastMessage.assessmentData.type === 'assessment_question'"
							class="bg-white rounded-xl p-4 border border-blue-200"
						>
							<!-- Debug info (remove in production) -->
							<div v-if="true" class="text-xs text-gray-500 mb-2 p-2 bg-gray-100 rounded">
								Debug: response_type = {{ lastMessage.assessmentData.question?.response_type || 'undefined' }}
								<br>Question structure: {{ JSON.stringify(lastMessage.assessmentData.question, null, 2) }}
							</div>

							<h4 class="font-medium text-blue-900 mb-3 text-sm sm:text-base">
								{{ lastMessage.assessmentData.question.question_text }}
							</h4>

							<!-- Scale Response Type -->
							<div
								v-if="lastMessage.assessmentData.question.response_type === 'scale'"
								class="space-y-3"
							>
								<p class="text-xs sm:text-sm text-blue-700">
									Pilih skala 1-10 (1 = sangat rendah, 10 = sangat tinggi)
								</p>
								<div class="grid grid-cols-5 sm:grid-cols-10 gap-2">
									<button
										v-for="scale in 10"
										:key="scale"
										@click="submitAssessmentResponse(scale)"
										class="w-8 h-8 sm:w-10 sm:h-10 rounded-full border-2 border-blue-300 text-blue-700 hover:bg-blue-100 hover:border-blue-500 transition-colors text-sm font-medium"
									>
										{{ scale }}
									</button>
								</div>
							</div>

							<!-- Text Response Type -->
							<div
								v-else-if="lastMessage.assessmentData.question.response_type === 'text'"
								class="space-y-3"
							>
								<textarea
									v-model="assessmentTextResponse"
									placeholder="Tuliskan jawaban Anda..."
									rows="3"
									class="w-full px-3 py-2 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
								></textarea>
								<button
									@click="submitAssessmentResponse(assessmentTextResponse)"
									:disabled="!assessmentTextResponse.trim()"
									class="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
								>
									Kirim Jawaban
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Typing Indicator -->
			<div v-if="ollamaIsProcessing" class="flex justify-start mb-1 sm:mb-2">
				<div class="flex items-start space-x-2 sm:space-x-3">
					<div
						class="w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center mt-1"
					>
						<Bot class="w-3 h-3 sm:w-3.5 sm:h-3.5 lg:w-4 lg:h-4 text-white" />
					</div>
					<div
						class="bg-white rounded-3xl rounded-tl-md px-4 py-3 shadow-sm border border-gray-100"
					>
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
		</div>

		<!-- Supportive Prompts Section -->
		<div v-if="showSupportivePrompts" class="bg-gradient-to-r from-blue-50 to-purple-50 border-t border-gray-200 p-3 sm:p-4 fixed bottom-80 left-0 right-0 mx-2 sm:mx-3 lg:mx-4 z-40 rounded-t-lg shadow-lg">
			<div class="mb-3">
				<h4 class="text-sm font-medium text-gray-700 mb-2">{{ t('supportive.howFeeling') }}</h4>
				<div class="flex flex-wrap gap-2">
					<button
						v-for="prompt in supportivePrompts"
						:key="prompt.id"
						@click="selectSupportivePrompt(prompt)"
						class="px-3 py-2 text-sm bg-white border border-gray-200 rounded-full hover:bg-blue-50 hover:border-blue-300 transition-all duration-200 shadow-sm"
					>
						{{ prompt.emoji }} {{ t(prompt.text) }}
					</button>
				</div>
			</div>
		</div>

		<!-- Emotion Selection Wheel -->
		<div v-if="showEmotionWheel" class="bg-white border-t border-gray-200 p-3 sm:p-4 fixed bottom-80 left-0 right-0 mx-2 sm:mx-3 lg:mx-4 z-40 rounded-t-lg shadow-lg">
			<div class="mb-3">
				<h4 class="text-sm font-medium text-gray-700 mb-3">{{ t('emotion.selectEmotion') }}</h4>
				<div class="grid grid-cols-4 gap-3">
					<button
						v-for="emotion in emotionOptions"
						:key="emotion.id"
						@click="selectEmotion(emotion)"
						:class="[
							'p-3 rounded-lg border-2 transition-all duration-200 text-center',
							selectedEmotion?.id === emotion.id
								? 'border-blue-500 bg-blue-50'
								: 'border-gray-200 hover:border-blue-300 hover:bg-blue-50'
						]"
					>
						<div class="text-2xl mb-1">{{ emotion.emoji }}</div>
						<div class="text-xs text-gray-600">{{ t(emotion.label) }}</div>
					</button>
				</div>
			</div>

			<!-- Emotion Intensity Scale -->
			<div v-if="selectedEmotion" class="mt-4">
				<h5 class="text-sm font-medium text-gray-700 mb-2">{{ t('emotion.intensity') }}</h5>
				<div class="flex items-center space-x-2">
					<span class="text-xs text-gray-500">{{ t('emotion.mild') }}</span>
					<input
						v-model="emotionIntensity"
						type="range"
						min="1"
						max="10"
						class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
					/>
					<span class="text-xs text-gray-500">{{ t('emotion.intense') }}</span>
					<span class="text-sm font-medium text-blue-600 min-w-[2rem]">{{ emotionIntensity }}</span>
				</div>
			</div>
		</div>

		<!-- Quick Response Buttons -->
		<div v-if="showQuickResponses && quickResponseOptions.length > 0" class="bg-gray-50 border-t border-gray-200 p-3 sm:p-4 fixed bottom-80 left-0 right-0 mx-2 sm:mx-3 lg:mx-4 z-40 rounded-t-lg shadow-lg">
			<div class="mb-2">
				<h4 class="text-sm font-medium text-gray-700 mb-3">{{ t('quickResponses.title') }}</h4>
				<div class="flex flex-wrap gap-2">
					<button
						v-for="response in quickResponseOptions"
						:key="response.id"
						@click="selectQuickResponse(response)"
						class="px-4 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-blue-50 hover:border-blue-400 transition-all duration-200 shadow-sm"
					>
						{{ t(response.text) }}
					</button>
				</div>
			</div>
		</div>

		<!-- Assessment Progress Indicator -->
		<div v-if="assessmentProgress && assessmentProgress.isActive" class="bg-blue-50 border-t border-blue-200 p-3 sm:p-4 fixed bottom-64 left-0 right-0 mx-2 sm:mx-3 lg:mx-4 z-40 rounded-t-lg shadow-lg">
			<div class="flex items-center justify-between mb-2">
				<h4 class="text-sm font-medium text-blue-700">{{ t('assessment.progress') }}</h4>
				<div class="flex items-center space-x-2">
					<button
						@click="pauseAssessment"
						class="p-1 text-blue-600 hover:text-blue-800 transition-colors"
						:title="t('assessment.pause')"
					>
						<Pause class="w-4 h-4" />
					</button>
					<button
						@click="goBackInAssessment"
						:disabled="!canGoBack"
						class="p-1 text-blue-600 hover:text-blue-800 disabled:text-gray-400 transition-colors"
						:title="t('assessment.goBack')"
					>
						<ArrowLeft class="w-4 h-4" />
					</button>
					<button
						@click="exitAssessment"
						class="p-1 text-red-600 hover:text-red-800 transition-colors"
						:title="t('assessment.exit')"
					>
						<X class="w-4 h-4" />
					</button>
				</div>
			</div>
			<div class="w-full bg-blue-200 rounded-full h-2">
				<div
					class="bg-blue-600 h-2 rounded-full transition-all duration-300"
					:style="{ width: assessmentProgress.percentage + '%' }"
				></div>
			</div>
			<div class="text-xs text-blue-600 mt-1">{{ assessmentProgress.currentQuestion }} / {{ assessmentProgress.totalQuestions }}</div>
		</div>

		<!-- Input Area -->
		<div
			class="bg-white border-t border-gray-200 p-3 sm:p-4 flex-shrink-0 z-50 fixed bottom-16 left-0 right-0 mx-2 sm:mx-3 lg:mx-4"
		>
			<!-- Mode Toggle and Helper Buttons -->
			<div class="flex items-center justify-between mb-3">
				<div class="flex items-center space-x-2">
					<button
						@click="setConversationMode('guided')"
						:class="[
							'px-3 py-1 text-sm rounded-full transition-all duration-200',
							conversationMode === 'guided'
								? 'bg-blue-500 text-white'
								: 'bg-gray-200 text-gray-700 hover:bg-gray-300'
						]"
					>
						{{ t('mode.guided') }}
					</button>
					<button
						@click="setConversationMode('free')"
						:class="[
							'px-3 py-1 text-sm rounded-full transition-all duration-200',
							conversationMode === 'free'
								? 'bg-blue-500 text-white'
								: 'bg-gray-200 text-gray-700 hover:bg-gray-300'
						]"
					>
						{{ t('mode.free') }}
					</button>
				</div>

				<!-- Helper Buttons -->
				<div class="flex items-center space-x-2">
					<button
						@click="toggleSupportivePrompts"
						:class="[
							'p-2 rounded-lg transition-all duration-200',
							showSupportivePrompts
								? 'bg-blue-500 text-white'
								: 'bg-gray-200 text-gray-600 hover:bg-gray-300'
						]"
						:title="t('supportive.toggle')"
					>
						<Heart class="w-4 h-4" />
					</button>
					<button
						@click="toggleEmotionWheel"
						:class="[
							'p-2 rounded-lg transition-all duration-200',
							showEmotionWheel
								? 'bg-purple-500 text-white'
								: 'bg-gray-200 text-gray-600 hover:bg-gray-300'
						]"
						:title="t('emotion.toggle')"
					>
						<Smile class="w-4 h-4" />
					</button>
					<button
						@click="toggleQuickResponses"
						:class="[
							'p-2 rounded-lg transition-all duration-200',
							showQuickResponses
								? 'bg-green-500 text-white'
								: 'bg-gray-200 text-gray-600 hover:bg-gray-300'
						]"
						:title="t('quickResponses.toggle')"
					>
						<MessageSquare class="w-4 h-4" />
					</button>
				</div>
			</div>
			<div class="flex items-end space-x-3">
				<!-- Voice Recording Button -->
				<button
					@click="toggleRecording"
					:class="[
						'flex-shrink-0 w-12 h-12 sm:w-12 sm:h-12 lg:w-12 lg:h-12 rounded-full flex items-center justify-center transition-colors shadow-sm min-h-[48px] min-w-[48px]',
						isRecording
							? 'bg-red-500 text-white animate-pulse'
							: 'bg-gray-100 text-gray-600 hover:bg-gray-200 active:bg-gray-300',
					]"
				>
					<Mic class="w-4 h-4 sm:w-5 sm:h-5" />
				</button>

				<!-- Text Input -->
				<div class="flex-1 relative">
					<textarea
						v-model="currentMessage"
						@keydown="handleKeyDown"
						@input="handleInputChange"
						:placeholder="getContextualPlaceholder()"
						rows="1"
						class="w-full px-4 py-3 pr-16 sm:pr-20 border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm sm:text-base bg-gray-50 focus:bg-white transition-colors"
						style="max-height: 120px"
					></textarea>

					<!-- Real-time Feedback Indicators -->
					<div v-if="showRealTimeFeedback && currentMessage.trim()" class="absolute right-14 sm:right-16 top-1/2 transform -translate-y-1/2">
						<div class="flex items-center space-x-1">
							<!-- Emotion Detection -->
							<div v-if="detectedEmotion" class="text-lg sm:text-xl" :title="t('emotion.detected')">{{ getEmotionEmoji(detectedEmotion) }}</div>
							<!-- Sentiment Indicators -->
							<div v-if="isTypingPositive" class="w-2 h-2 bg-green-400 rounded-full animate-pulse" :title="t('feedback.positive')"></div>
							<div v-else-if="isTypingNegative" class="w-2 h-2 bg-red-400 rounded-full animate-pulse" :title="t('feedback.needsSupport')"></div>
							<div v-else-if="currentMessage.trim()" class="w-2 h-2 bg-blue-400 rounded-full animate-pulse" :title="t('feedback.neutral')"></div>
							<!-- Crisis Detection Warning -->
							<div v-if="potentialCrisisDetected" class="w-2 h-2 bg-orange-500 rounded-full animate-pulse" :title="t('feedback.crisis')"></div>
						</div>
					</div>

					<!-- Empathy Validation Badge -->
					<div v-if="showEmpathyValidation" class="absolute right-2 sm:right-3 top-1/2 transform -translate-y-1/2">
						<div class="bg-green-100 text-green-600 px-2 py-1 rounded-full text-xs flex items-center space-x-1">
							<Heart class="w-3 h-3" />
							<span>{{ t('empathy.validated') }}</span>
						</div>
					</div>

					<!-- Emoji Button -->
					<button
						v-if="!showEmpathyValidation"
						@click="toggleEmotionWheel"
						class="absolute right-2 sm:right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 p-2 rounded-full hover:bg-gray-100 transition-colors"
					>
						<Smile class="w-4 h-4 sm:w-5 sm:h-5" />
					</button>
				</div>

				<!-- Send Button -->
				<button
					@click="handleSendMessage"
					:disabled="!currentMessage.trim() || isSending"
					:class="[
						'flex-shrink-0 w-12 h-12 sm:w-12 sm:h-12 lg:w-12 lg:h-12 rounded-full flex items-center justify-center transition-colors shadow-sm min-h-[48px] min-w-[48px]',
						currentMessage.trim() && !isSending
							? 'bg-blue-500 text-white hover:bg-blue-600 active:bg-blue-700'
							: 'bg-gray-100 text-gray-400 cursor-not-allowed',
					]"
				>
					<Send v-if="!isSending" class="w-4 h-4 sm:w-5 sm:h-5" />
					<div
						v-else
						class="w-4 h-4 sm:w-5 sm:h-5 border-2 border-white border-t-transparent rounded-full animate-spin"
					></div>
				</button>
			</div>
		</div>

		<!-- Privacy Settings Modal -->
		<div
			v-if="showPrivacySettings"
			class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-2 sm:p-4"
		>
			<div
				class="bg-white rounded-2xl p-3 sm:p-4 lg:p-6 w-full max-w-xs sm:max-w-sm lg:max-w-md"
			>
				<div class="flex items-center justify-between mb-3 sm:mb-4">
					<h3
						class="text-sm sm:text-base lg:text-lg font-bold text-gray-900 truncate"
					>
						Pengaturan Privasi
					</h3>
					<button
						@click="showPrivacySettings = false"
						class="p-1.5 sm:p-2 hover:bg-gray-100 rounded flex-shrink-0"
					>
						<X class="w-4 h-4 sm:w-5 sm:h-5 text-gray-500" />
					</button>
				</div>

				<div class="space-y-3 sm:space-y-4">
					<div class="flex items-center justify-between">
						<span class="text-xs sm:text-sm lg:text-base text-gray-700"
							>Simpan Riwayat Chat</span
						>
						<input
							type="checkbox"
							v-model="privacySettings.saveHistory"
							class="rounded"
						/>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-xs sm:text-sm lg:text-base text-gray-700"
							>Analisis Emosi</span
						>
						<input
							type="checkbox"
							v-model="privacySettings.emotionAnalysis"
							class="rounded"
						/>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-xs sm:text-sm lg:text-base text-gray-700"
							>Deteksi Krisis</span
						>
						<input
							type="checkbox"
							v-model="privacySettings.crisisDetection"
							class="rounded"
						/>
					</div>
				</div>

				<div class="mt-4 sm:mt-6 pt-3 sm:pt-4 border-t border-gray-200">
					<button
						@click="requestDataDeletion"
						class="w-full py-2 px-3 sm:px-4 bg-red-600 hover:bg-red-700 text-white rounded-lg text-xs sm:text-sm"
					>
						Hapus Semua Data Saya
					</button>
					<p class="text-xs text-gray-500 mt-2 text-center">
						Data dapat dipulihkan dalam 30 hari setelah penghapusan
					</p>
				</div>
			</div>
		</div>

		<!-- Emergency Info Modal -->
		<div
			v-if="showEmergencyInfo"
			class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-2 sm:p-4"
		>
			<div
				class="bg-white rounded-2xl p-3 sm:p-4 lg:p-6 w-full max-w-xs sm:max-w-sm lg:max-w-md"
			>
				<div class="flex items-center justify-between mb-3 sm:mb-4">
					<h3
						class="text-sm sm:text-base lg:text-lg font-bold text-gray-900 truncate"
					>
						Bantuan Darurat
					</h3>
					<button
						@click="showEmergencyInfo = false"
						class="p-1.5 sm:p-2 hover:bg-gray-100 rounded flex-shrink-0"
					>
						<X class="w-4 h-4 sm:w-5 sm:h-5 text-gray-500" />
					</button>
				</div>

				<div class="space-y-3 sm:space-y-4">
					<div class="text-center">
						<AlertTriangle
							class="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 text-red-500 mx-auto mb-2"
						/>
						<p class="text-xs sm:text-sm lg:text-base text-gray-700">
							Jika Anda atau seseorang yang Anda kenal dalam bahaya segera,
							hubungi:
						</p>
					</div>

					<div class="space-y-2 sm:space-y-3">
						<a
							href="tel:112"
							class="block w-full p-2 sm:p-3 bg-red-50 border border-red-200 rounded-lg text-center"
						>
							<div
								class="font-medium text-red-900 text-xs sm:text-sm lg:text-base"
							>
								🚨 Emergency: 112
							</div>
							<div class="text-xs sm:text-sm text-red-700">
								Layanan darurat 24/7
							</div>
						</a>

						<a
							href="tel:119"
							class="block w-full p-2 sm:p-3 bg-blue-50 border border-blue-200 rounded-lg text-center"
						>
							<div
								class="font-medium text-blue-900 text-xs sm:text-sm lg:text-base"
							>
								💬 Crisis Hotline: 119 ext 8
							</div>
							<div class="text-xs sm:text-sm text-blue-700">
								Konseling krisis mental
							</div>
						</a>

						<a
							href="https://wa.me/6281119854854"
							class="block w-full p-2 sm:p-3 bg-green-50 border border-green-200 rounded-lg text-center"
						>
							<div
								class="font-medium text-green-900 text-xs sm:text-sm lg:text-base"
							>
								💚 Into The Light: WhatsApp
							</div>
							<div class="text-xs sm:text-sm text-green-700">
								Support via chat
							</div>
						</a>
					</div>

					<p class="text-xs text-gray-600 text-center">
						Ingat: Mencari bantuan adalah tanda kekuatan, bukan kelemahan.
					</p>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed, watch } from "vue";
import {
	Bot,
	Heart,
	MoreVertical,
	Mic,
	MicOff,
	Smile,
	Send,
	X,
	AlertTriangle,
	Volume2,
	Zap,
	Eye,
	Globe,
	Pause,
	ArrowLeft,
	Check,
	ChevronDown,
	Settings,
	Menu,
	Download,
	Copy,
	Trash2,
	Phone,
	MessageCircle,
	HelpCircle,
	MessageSquare,
	Lightbulb,
	User,
} from "lucide-vue-next";

// I18n composable
const { t, locale, locales, setLocale } = useI18n();

// Set layout
definePageMeta({
	layout: "app",
});

// Enhanced Ollama Chat integration with semantic search
const {
	sendMessage,
	sendMessageStream,
	isProcessing: ollamaIsProcessing,
	isStreaming: ollamaIsStreaming,
	error: ollamaError,
	isConnected,
	sessionId,
	messages: ollamaMessages,
	addMessage: addOllamaMessage,
	clearMessages: clearOllamaMessages,
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
	acceptAssessmentSuggestion,
	declineAssessmentSuggestion,
	detectedProblemCategory,
	shouldShowAssessmentSuggestion,
} = useOllamaChat();

// Refs
const messagesContainer = ref(null);
const menuContainer = ref(null);
const currentMessage = ref("");
const isSending = ref(false);
const isRecording = ref(false);
const currentMode = ref("help");
const showMenu = ref(false);
const showCrisisAlert = ref(false);
const showPrivacySettings = ref(false);
const showEmergencyInfo = ref(false);
const detectedEmotion = ref(null);
const windowWidth = ref(
	typeof window !== "undefined" ? window.innerWidth : 1024
);

// Speech Mode Variables
const isSpeechMode = ref(false);
const isFluidConversationActive = ref(false);
const fluidConversationCount = ref(0);
const maxFluidConversations = ref(10);
const currentSpeechText = ref("");
const speechMessages = ref([]);
const speechDuration = ref(0);
const speechStartTime = ref(null);
const showTranscriptView = ref(false);
const conversationTranscript = ref([]);
const assessmentTextResponse = ref("");

// Enhanced UI State Variables
const showSupportivePrompts = ref(true);
const showEmotionWheel = ref(false);
const selectedEmotion = ref(null);
const emotionIntensity = ref(5);
const showQuickResponses = ref(false);
const showRealTimeFeedback = ref(true);
const showEmpathyValidation = ref(false);
const isTypingPositive = ref(false);
const isTypingNegative = ref(false);
const potentialCrisisDetected = ref(false);
const conversationMode = ref('guided'); // 'guided' or 'free'
const assessmentPaused = ref(false);
const canNavigateBack = ref(false);
const showProgressIndicator = ref(true);

// Speech Recognition Variables
const isListening = ref(false);
const isProcessingSpeech = ref(false);
const isGeneratingResponse = ref(false);
const speechRecognition = ref(null);
const speechSynthesis = ref(null);
const isSpeechSupported = ref(false);

// Computed Properties
const isMobile = computed(() => windowWidth.value < 768);
const isExtraSmall = computed(() => windowWidth.value < 480);
const speechStatus = computed(() => {
	try {
		if (isListening.value) return `- ${t('status.listening')}`;
		if (isProcessingSpeech.value) return `- ${t('status.processing')}`;
		if (isGeneratingResponse.value) return `- ${t('status.responding')}`;
		return `- ${t('status.ready')}`;
	} catch (error) {
		console.warn('Translation error in speechStatus:', error);
		return '- Ready';
	}
});

const privacySettings = ref({
	saveHistory: true,
	emotionAnalysis: true,
	crisisDetection: true,
});

// Quick intent buttons for first-time users
const quickIntents = computed(() => {
	try {
		return [
			{
				id: 1,
				emoji: "😰",
				label: t('quickIntents.anxious.label'),
				message: t('quickIntents.anxious.message'),
				mode: "help",
			},
			{
				id: 2,
				emoji: "😢",
				label: t('quickIntents.sad.label'),
				message: t('quickIntents.sad.message'),
				mode: "help",
			},
			{
				id: 3,
				emoji: "💡",
				label: t('quickIntents.tips.label'),
				message: t('quickIntents.tips.message'),
				mode: "tips",
			},
			{
				id: 4,
				emoji: "💬",
				label: t('quickIntents.chat.label'),
				message: t('quickIntents.chat.message'),
				mode: "chat",
			},
		];
	} catch (error) {
		console.warn('Translation error in quickIntents:', error);
		return [
			{
				id: 1,
				emoji: "😰",
				label: "I'm feeling anxious...",
				message: "I'm feeling anxious and don't know what to do. Can you help me?",
				mode: "help",
			},
			{
				id: 2,
				emoji: "😢",
				label: "I'm sad today",
				message: "I'm feeling sad today and need someone to talk to.",
				mode: "help",
			},
			{
				id: 3,
				emoji: "💡",
				label: "Tips for stress",
				message: "Can you give me some tips to manage stress?",
				mode: "tips",
			},
			{
				id: 4,
				emoji: "💬",
				label: "I want to share",
				message: "I want to share what's on my mind today.",
				mode: "chat",
			},
		];
	}
});

// Crisis keywords for detection
const crisisKeywords = [
	"bunuh diri",
	"mengakhiri hidup",
	"tidak ingin hidup",
	"menyakiti diri",
	"suicide",
	"self harm",
	"hurt myself",
	"end my life",
	"kill myself",
];

// Methods
const getModeDescription = (mode) => {
	try {
		switch (mode) {
			case "help":
				return t('modeDescriptions.help');
			case "tips":
				return t('modeDescriptions.tips');
			case "chat":
				return t('modeDescriptions.chat');
			default:
				return t('modeDescriptions.help');
		}
	} catch (error) {
		console.warn('Translation error in getModeDescription:', error);
		switch (mode) {
			case "help":
				return "Get help and support for mental health issues";
			case "tips":
				return "Receive daily tips to improve your mental wellbeing";
			case "chat":
				return "Chat freely about anything on your mind";
			default:
				return "Get help and support for mental health issues";
		}
	}
};

// Language switching function
const switchLanguage = () => {
	const newLocale = locale.value === 'id' ? 'en' : 'id';
	setLocale(newLocale);
};

const getEmotionEmoji = (emotion) => {
	const emotionMap = {
		sad: "😢",
		anxious: "😰",
		angry: "😠",
		happy: "😊",
		neutral: "😐",
		stressed: "😵",
		hopeful: "🙂",
	};
	return emotionMap[emotion] || "😐";
};

const detectEmotion = () => {
	if (!privacySettings.value.emotionAnalysis) return;

	const message = currentMessage.value.toLowerCase();

	// Simple emotion detection based on keywords
	if (
		message.includes("sedih") ||
		message.includes("sad") ||
		message.includes("down")
	) {
		detectedEmotion.value = "sad";
	} else if (
		message.includes("cemas") ||
		message.includes("anxious") ||
		message.includes("worry")
	) {
		detectedEmotion.value = "anxious";
	} else if (
		message.includes("marah") ||
		message.includes("angry") ||
		message.includes("frustasi")
	) {
		detectedEmotion.value = "angry";
	} else if (
		message.includes("bahagia") ||
		message.includes("happy") ||
		message.includes("senang")
	) {
		detectedEmotion.value = "happy";
	} else if (
		message.includes("stress") ||
		message.includes("overwhelmed") ||
		message.includes("capek")
	) {
		detectedEmotion.value = "stressed";
	} else {
		detectedEmotion.value = "neutral";
	}
};

const checkForCrisis = (message) => {
	if (!privacySettings.value.crisisDetection) return false;

	const lowerMessage = message.toLowerCase();
	return crisisKeywords.some((keyword) => lowerMessage.includes(keyword));
};

const handleSendMessage = async () => {
	console.log('🎯 handleSendMessage called with:', {
		message: currentMessage.value,
		isSending: isSending.value,
		messagesCount: ollamaMessages.value.length,
		currentMode: currentMode.value
	});

	if (!currentMessage.value.trim() || isSending.value) {
		console.log('⚠️ Message sending blocked:', {
			emptyMessage: !currentMessage.value.trim(),
			isSending: isSending.value
		});
		return;
	}

	const userMessage = {
		id: `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
		text: currentMessage.value.trim(),
		sender: "user",
		timestamp: new Date(),
		emotionTone: detectedEmotion.value,
	};

	// Check for crisis keywords
	if (checkForCrisis(userMessage.text)) {
		showCrisisAlert.value = true;
	}

	addOllamaMessage(userMessage);
	const messageText = currentMessage.value;
	const messageEmotion = detectedEmotion.value;
	currentMessage.value = "";
	detectedEmotion.value = null;

	await scrollToBottom();

	isSending.value = true;

	try {
		console.log('🚀 Starting message processing with:', {
			messageText,
			messageEmotion,
			mode: currentMode.value,
			sessionId: sessionId.value
		});

		// Create AI message placeholder for streaming
		const aiMessageId = `ai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
		const aiMessage = {
			id: aiMessageId,
			text: "",
			sender: "ai",
			timestamp: new Date(),
			detectedEmotion: messageEmotion,
			isStreaming: true,
		};
		console.log('📝 Created AI message placeholder:', aiMessage);
		addOllamaMessage(aiMessage);
		await scrollToBottom();

		// Use WebSocket streaming instead of API call
		console.log('📡 Calling sendMessageStream...');
		await sendMessageStream(
			messageText,
			{
				emotion: messageEmotion,
				mode: currentMode.value,
				sessionId: sessionId.value,
				preferredLanguage: locale.value,
			},
			(chunk) => {
				console.log('📦 Received chunk:', { chunk, length: chunk?.length });
				// Update the AI message with streaming content
				const messageIndex = ollamaMessages.value.findIndex(msg => msg.id === aiMessageId);
				if (messageIndex !== -1) {
					ollamaMessages.value[messageIndex].text += chunk;
					console.log('✏️ Updated AI message text:', {
						messageIndex,
						totalLength: ollamaMessages.value[messageIndex].text.length,
						chunkAdded: chunk
					});
					scrollToBottom();
				} else {
					console.warn('⚠️ Could not find AI message to update:', aiMessageId);
				}
			},
			(finalResponse) => {
				console.log('✅ Received final response:', finalResponse);
				// Update the AI message with final data
				const messageIndex = ollamaMessages.value.findIndex(msg => msg.id === aiMessageId);
				if (messageIndex !== -1) {
					ollamaMessages.value[messageIndex].isStreaming = false;
					if (finalResponse) {
						// Only set message text if no chunks were received (direct complete message)
						// Don't overwrite text that was built from chunks
						if (finalResponse.message && ollamaMessages.value[messageIndex].text.length === 0) {
							ollamaMessages.value[messageIndex].text = finalResponse.message;
							console.log('📝 Set message text from finalResponse (no chunks received):', {
								messageIndex,
								textLength: finalResponse.message.length
							});
						} else if (ollamaMessages.value[messageIndex].text.length > 0) {
							console.log('📝 Keeping chunked text, not overwriting with finalResponse.message:', {
								messageIndex,
								chunkTextLength: ollamaMessages.value[messageIndex].text.length,
								finalResponseLength: finalResponse.message?.length || 0
							});
						}

						// Set metadata
						ollamaMessages.value[messageIndex].sentiment = finalResponse.sentiment;
						ollamaMessages.value[messageIndex].isCrisis = finalResponse.isCrisis;
						ollamaMessages.value[messageIndex].problemCategory = finalResponse.problemCategory;
						ollamaMessages.value[messageIndex].suggestions = finalResponse.suggestions;
						ollamaMessages.value[messageIndex].assessmentQuestions = finalResponse.assessmentQuestions;
						ollamaMessages.value[messageIndex].assessmentData = finalResponse.assessmentData;
						ollamaMessages.value[messageIndex].showAssessmentTransition = finalResponse.showAssessmentTransition;
						ollamaMessages.value[messageIndex].contextAnalysis = finalResponse.contextAnalysis;
						ollamaMessages.value[messageIndex].suggestedCategory = finalResponse.suggestedCategory;
						ollamaMessages.value[messageIndex].subCategoryId = finalResponse.subCategoryId;
						console.log('🏁 Finalized AI message with metadata:', {
							messageIndex,
							finalTextLength: ollamaMessages.value[messageIndex].text.length,
							metadata: finalResponse
						});
					} else {
						console.log('🏁 Finalized AI message without metadata:', {
							messageIndex,
							finalTextLength: ollamaMessages.value[messageIndex].text.length
						});
					}
					scrollToBottom();
				} else {
					console.warn('⚠️ Could not find AI message to finalize:', aiMessageId);
				}
			},
			(newMessageData) => {
				console.log('🆕 Creating new AI message for assessment question:', newMessageData);

				// Remove any loading messages
				const loadingMessageIndex = ollamaMessages.value.findIndex(msg =>
					msg.sender === 'ai' && msg.isStreaming && msg.text.includes('Memproses')
				);
				if (loadingMessageIndex !== -1) {
					ollamaMessages.value.splice(loadingMessageIndex, 1);
					console.log('🗑️ Removed loading message');
				}

				// Create a new AI message for assessment questions
				const newAiMessageId = `ai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
				addOllamaMessage({
					id: newAiMessageId,
					text: newMessageData.message || '',
					sender: "ai",
					timestamp: new Date(),
					isStreaming: false,
					sentiment: newMessageData.sentiment,
					isCrisis: newMessageData.isCrisis,
					problemCategory: newMessageData.problemCategory,
					suggestions: newMessageData.suggestions,
					assessmentQuestions: newMessageData.assessmentQuestions,
					assessmentData: newMessageData.assessmentData,
					stage: newMessageData.stage,
					progress: newMessageData.progress
				});
				scrollToBottom();
			}
		);
		console.log('📡 sendMessageStream call completed');
	} catch (error) {
		console.error("❌ Error sending message:", error);
		console.error("❌ Error details:", {
			message: error.message,
			stack: error.stack,
			name: error.name,
			cause: error.cause
		});
		const errorText = await generateFallbackResponse('technical_error')
		const errorMessage = {
			id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
			text: errorText,
			sender: "ai",
			timestamp: new Date(),
		};
		addOllamaMessage(errorMessage);
	} finally {
		isSending.value = false;
		await scrollToBottom();
	}
};

const generateCounselorResponse = (userMessage, emotion, mode) => {
	// Crisis response takes priority
	if (checkForCrisis(userMessage)) {
		return `Saya sangat peduli dengan keselamatan Anda. Perasaan yang Anda alami sekarang sangat berat, tapi Anda tidak sendirian. Sudah tepat Anda berbagi dengan saya.

Jika Anda merasa dalam bahaya segera, tolong hubungi:
• Emergency: 112
• Crisis Hotline: 119 ext 8

Sementara itu, coba fokus pada pernapasan Anda. Tarik napas perlahan selama 4 detik, tahan 4 detik, lalu hembuskan 4 detik. Ulangi sampai Anda merasa sedikit lebih tenang.

Apakah Anda mau cerita lebih lanjut tentang apa yang membuat Anda merasa seperti ini?`;
	}

	// Emotion-based responses
	const responses = {
		help: {
			sad: [
				`Saya mendengar bahwa Anda sedang merasa sedih. Perasaan ini valid dan manusiawi. Tidak apa-apa untuk merasa sedih.

Bisakah Anda ceritakan lebih detail tentang apa yang membuat Anda merasa seperti ini? Kadang berbagi beban bisa membantu meringankan perasaan.

Ingat: perasaan sedih ini tidak akan bertahan selamanya, meski sekarang terasa sangat berat.`,

				`Terima kasih sudah berbagi perasaan Anda dengan saya. Kesedihan yang Anda rasakan adalah respons natural terhadap situasi yang sulit.

Mari kita jelajahi bersama:
• Apa yang paling berat Anda rasakan sekarang?
• Apakah ada pemicu khusus untuk kesedihan ini?
• Bagaimana biasanya Anda mengatasi perasaan seperti ini?

Saya di sini untuk mendengarkan dan membantu Anda menemukan cara untuk merasa lebih baik.`,
			],
			anxious: [
				`Kecemasan yang Anda rasakan pasti sangat tidak nyaman. Saya memahami betapa mengganggunya perasaan ini.

Mari kita coba teknik grounding 5-4-3-2-1:
• 5 hal yang bisa Anda lihat
• 4 hal yang bisa Anda sentuh
• 3 hal yang bisa Anda dengar
• 2 hal yang bisa Anda cium
• 1 hal yang bisa Anda rasakan

Teknik ini bisa membantu mengembalikan fokus Anda ke saat ini. Bagaimana perasaan Anda setelah mencobanya?`,

				`Kecemasan bisa terasa sangat overwhelming. Yang Anda rasakan sekarang adalah respons alami tubuh terhadap sesuatu yang dianggap mengancam.

Coba tarik napas dalam-dalam bersama saya:
Tarik napas selama 4 detik... tahan 4 detik... hembuskan 6 detik...

Apa yang paling Anda cemaskan saat ini? Mari kita pecahkan kekhawatiran itu menjadi bagian-bagian yang lebih mudah dikelola.`,
			],
		},
		tips: {
			default: [
				`Berikut beberapa tips harian untuk kesehatan mental yang bisa Anda coba:

🌅 **Pagi**: Mulai dengan 5 menit meditasi atau jurnal syukur
🏃 **Siang**: Jalan kaki singkat atau stretching untuk refresh pikiran
🌙 **Malam**: Rutinitas tidur yang konsisten, hindari gadget 1 jam sebelum tidur

💡 **Bonus tip**: Praktikkan "self-compassion" - perlakukan diri Anda dengan kebaikan yang sama seperti Anda memperlakukan teman baik.

Mana dari tips ini yang ingin Anda coba lebih dulu?`,

				`Tips manajemen stress untuk hari ini:

🧘 **Mindfulness**: Luangkan 2 menit untuk fokus sepenuhnya pada satu aktivitas
🎯 **Prioritas**: Buat daftar 3 hal terpenting hari ini, abaikan yang lain
💬 **Koneksi**: Hubungi satu orang yang Anda sayangi
🚶 **Gerakan**: 10-15 menit aktivitas fisik ringan

Ingat: kemajuan kecil setiap hari lebih baik daripada perubahan drastis yang tidak sustainable.

Apa yang paling sulit Anda kelola dari stress harian Anda?`,
			],
		},
		chat: {
			default: [
				`Terima kasih sudah mau berbagi dengan saya. Saya di sini untuk mendengarkan tanpa menghakimi.

Apa yang ada di pikiran Anda hari ini? Ceritakan apa saja yang Anda mau - tentang hari Anda, perasaan Anda, atau hal apapun yang ingin Anda bagikan.

Ingat, tidak ada yang terlalu kecil atau terlalu besar untuk dibicarakan di sini.`,

				`Saya senang Anda memilih untuk berbagi dengan saya. Kadang hanya dengan bercerita, beban di hati bisa terasa lebih ringan.

Bagaimana perasaan Anda secara umum hari ini? Ada yang ingin Anda rayakan atau keluhkan?

Saya mendengarkan dengan perhatian penuh.`,
			],
		},
	};

	const modeResponses = responses[mode] || responses.help;
	const emotionResponses =
		modeResponses[emotion] ||
		modeResponses.default ||
		modeResponses[Object.keys(modeResponses)[0]];

	return emotionResponses[Math.floor(Math.random() * emotionResponses.length)];
};

const sendQuickMessage = (message, mode) => {
	currentMode.value = mode;
	currentMessage.value = message;
	handleSendMessage();
};

const handleModeChange = () => {
	showMenu.value = false;
	// Could add mode-specific welcome message
};

const handleKeyDown = (event) => {
	if (event.key === "Enter" && !event.shiftKey) {
		event.preventDefault();
		handleSendMessage();
	}
};

const scrollToBottom = async () => {
	await nextTick();
	if (messagesContainer.value) {
		messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
	}
};

const toggleRecording = () => {
	isRecording.value = !isRecording.value;
	// Implement voice recording logic
};

const clearHistory = () => {
	if (
		confirm(
			"Apakah Anda yakin ingin menghapus semua riwayat chat? Tindakan ini tidak dapat dibatalkan."
		)
	) {
		clearOllamaMessages();
	}
};

const exportChat = () => {
	const chatData = {
		timestamp: new Date().toISOString(),
		messages: ollamaMessages.value,
	};
	const blob = new Blob([JSON.stringify(chatData, null, 2)], {
		type: "application/json",
	});
	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = `mindcare-chat-${new Date().toISOString().split("T")[0]}.json`;
	a.click();
};

const requestDataDeletion = () => {
	if (
		confirm(
			"Ini akan menghapus SEMUA data Anda termasuk riwayat chat, preferensi, dan hasil assessment. Data dapat dipulihkan dalam 30 hari. Lanjutkan?"
		)
	) {
		// Implement data deletion logic
		localStorage.clear();
		clearOllamaMessages();
		showPrivacySettings.value = false;
		alert(
			"Data Anda telah dijadwalkan untuk dihapus. Anda dapat memulihkannya dalam 30 hari ke depan."
		);
	}
};

const callEmergency = () => {
	window.location.href = "tel:112";
};

const dismissCrisisAlert = () => {
	showCrisisAlert.value = false;
};

const formatTime = (timestamp) => {
	if (!timestamp) return "";

	// Handle both Date objects and ISO strings
	const date = timestamp instanceof Date ? timestamp : new Date(timestamp);

	// Check if the date is valid
	if (isNaN(date.getTime())) return "";

	return new Intl.DateTimeFormat("id-ID", {
		hour: "2-digit",
		minute: "2-digit",
	}).format(date);
};

// Auto-resize textarea
const autoResize = (event) => {
	const textarea = event.target;
	textarea.style.height = "auto";
	textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
};

const toggleSpeechMode = () => {
	if (!isSpeechMode.value) {
		// Initialize speech mode
		initializeSpeechRecognition();
		speechStartTime.value = Date.now();
	} else {
		// End speech mode and save transcript
		endSpeechConversation();
	}
	isSpeechMode.value = !isSpeechMode.value;
};

const initializeSpeechRecognition = () => {
	if (typeof window !== "undefined") {
		const SpeechRecognition =
			window.SpeechRecognition || window.webkitSpeechRecognition;
		const SpeechSynthesisUtterance = window.SpeechSynthesisUtterance;

		if (SpeechRecognition && SpeechSynthesisUtterance) {
			isSpeechSupported.value = true;

			speechRecognition.value = new SpeechRecognition();
			speechRecognition.value.continuous = false;
			speechRecognition.value.interimResults = false;
			speechRecognition.value.lang = "id-ID";

			speechRecognition.value.onstart = () => {
				isListening.value = true;
				currentSpeechText.value = "Mendengarkan...";
			};

			speechRecognition.value.onresult = async (event) => {
				const transcript = event.results[0][0].transcript;
				currentSpeechText.value = transcript;
				isListening.value = false;
				isProcessingSpeech.value = true;

				// Add user message to speech messages
				addSpeechMessage(transcript, "user");

				// Generate AI response
				await generateSpeechResponse(transcript);

				// Auto-continue in fluid mode
				if (
					isFluidConversationActive.value &&
					fluidConversationCount.value < maxFluidConversations.value
				) {
					setTimeout(() => {
						if (isSpeechMode.value) {
							startVoiceInput();
						}
					}, 2000); // Wait 2 seconds before listening again
				}
			};

			speechRecognition.value.onerror = (event) => {
				console.error("Speech recognition error:", event.error);
				isListening.value = false;
				isProcessingSpeech.value = false;
				currentSpeechText.value = "Error: " + event.error;
			};

			speechRecognition.value.onend = () => {
				isListening.value = false;
			};
		} else {
			isSpeechSupported.value = false;
		}
	}
};

const startVoiceInput = () => {
	if (!speechRecognition.value || isListening.value || isProcessingSpeech.value)
		return;

	try {
		currentSpeechText.value = "";
		speechRecognition.value.start();
	} catch (error) {
		console.error("Error starting speech recognition:", error);
	}
};

const stopVoiceInput = () => {
	if (speechRecognition.value && isListening.value) {
		speechRecognition.value.stop();
		isListening.value = false;
	}
};

const addSpeechMessage = (text, sender) => {
	const message = {
		text,
		sender,
		time: formatTime(new Date()),
		timestamp: new Date(),
	};

	speechMessages.value.push(message);
	conversationTranscript.value.push(message);

	if (sender === "user") {
		fluidConversationCount.value++;
	}
};

const generateSpeechResponse = async (userMessage) => {
	isGeneratingResponse.value = true;

	try {
		// Check for crisis keywords
		if (checkForCrisis(userMessage)) {
			showCrisisAlert.value = true;
		}

		// Prepare message history for context
		const messageHistory = speechMessages.value.map((msg) => ({
			role: msg.sender === "user" ? "user" : "assistant",
			content: msg.text,
		}));

		// Generate response using the same logic as text chat
		const aiResponse = generateCounselorResponse(
			userMessage,
			detectedEmotion.value,
			currentMode.value
		);

		// Add AI response to speech messages
		addSpeechMessage(aiResponse, "ai");

		// Convert to speech
		await speakText(aiResponse);
	} catch (error) {
		console.error("Error generating speech response:", error);
		const errorMessage = await generateFallbackResponse('speech_error');
		addSpeechMessage(errorMessage, "ai");
		await speakText(errorMessage);
	} finally {
		isProcessingSpeech.value = false;
		isGeneratingResponse.value = false;
		currentSpeechText.value = "";
	}
};

const speakText = (text) => {
	return new Promise((resolve) => {
		if (typeof window !== "undefined" && window.speechSynthesis) {
			// Cancel any ongoing speech
			window.speechSynthesis.cancel();

			const utterance = new SpeechSynthesisUtterance(text);
			utterance.lang = "id-ID";
			utterance.rate = 0.9;
			utterance.pitch = 1;
			utterance.volume = 1;

			utterance.onend = () => {
				resolve();
			};

			utterance.onerror = (error) => {
				console.error("Speech synthesis error:", error);
				resolve();
			};

			window.speechSynthesis.speak(utterance);
		} else {
			resolve();
		}
	});
};

const toggleFluidConversation = () => {
	isFluidConversationActive.value = !isFluidConversationActive.value;

	if (isFluidConversationActive.value) {
		fluidConversationCount.value = 0;
	}
};

const endSpeechConversation = () => {
	// Stop any ongoing speech recognition
	if (speechRecognition.value && isListening.value) {
		speechRecognition.value.stop();
	}

	// Stop any ongoing speech synthesis
	if (typeof window !== "undefined" && window.speechSynthesis) {
		window.speechSynthesis.cancel();
	}

	// Calculate duration
	if (speechStartTime.value) {
		speechDuration.value = Math.floor(
			(Date.now() - speechStartTime.value) / 1000
		);
	}

	// Reset states
	isSpeechMode.value = false;
	isFluidConversationActive.value = false;
	isListening.value = false;
	isProcessingSpeech.value = false;
	isGeneratingResponse.value = false;
	currentSpeechText.value = "";

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

const toggleTranscriptPreview = () => {
	showTranscriptView.value = true;
};

const exportTranscript = () => {
	const transcriptData = {
		timestamp: new Date().toISOString(),
		duration: speechDuration.value,
		messages: conversationTranscript.value,
		mode: currentMode.value,
	};

	const blob = new Blob([JSON.stringify(transcriptData, null, 2)], {
		type: "application/json",
	});
	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = `voice-conversation-${
		new Date().toISOString().split("T")[0]
	}.json`;
	a.click();
	URL.revokeObjectURL(url);
};

const copyTranscriptToChat = () => {
	// Copy all transcript messages to the main chat
	conversationTranscript.value.forEach((message) => {
		addOllamaMessage({
			id: `transcript_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
			text: message.text,
			sender: message.sender,
			timestamp: message.timestamp,
			emotionTone: message.sender === "user" ? detectedEmotion.value : null,
		});
	});

	showTranscriptView.value = false;

	// Scroll to bottom of main chat
	nextTick(() => {
		scrollToBottom();
	});
};

const formatDuration = (seconds) => {
	const minutes = Math.floor(seconds / 60);
	const remainingSeconds = seconds % 60;
	return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
};

// Assessment transition handlers
const acceptAssessment = async (message) => {
	try {
		// Hide the assessment suggestion in the message
		message.showAssessmentTransition = false;

		// Start the assessment using the detected problem category
		const result = await acceptAssessmentSuggestion();

		if (result) {
			// Add a system message indicating assessment has started
			addOllamaMessage({
				id: `assessment_start_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
				text: `Assessment untuk ${detectedProblemCategory.value} telah dimulai. Mari kita lanjutkan dengan pertanyaan terstruktur.`,
				sender: "ai",
				timestamp: new Date(),
			});

			await scrollToBottom();
		}
	} catch (error) {
		console.error("Error starting assessment:", error);
	}
};

const declineAssessment = async (message) => {
	// Hide the assessment suggestion in the message
	message.showAssessmentTransition = false;

	// Decline the assessment suggestion
	declineAssessmentSuggestion();

	// Generate dynamic response for assessment decline
	const declineResponse = await generateFallbackResponse('assessment_decline')
	addOllamaMessage({
		id: `assessment_decline_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
		text: declineResponse,
		sender: "ai",
		timestamp: new Date(),
	});

	nextTick(() => {
		scrollToBottom();
	});
};

// Generate fallback response when backend is unavailable
const generateFallbackResponse = async (context) => {
	try {
		// Try to get a dynamic response from backend
		const response = await $fetch('/api/v1/chat', {
			method: 'POST',
			body: {
				message: `fallback_${context}`,
				client_id: clientId.value,
				session_data: {
					preferredLanguage: locale.value,
					mode: currentMode.value,
					context: context
				},
				use_flow: true
			}
		})
		return response.message
	} catch (error) {
		console.error('Fallback generation failed:', error)
		// Ultimate fallback based on locale
		if (locale.value === 'id') {
			return 'Saya di sini untuk membantu Anda. Mari kita lanjutkan percakapan.'
		} else {
			return 'I\'m here to help you. Let\'s continue our conversation.'
		}
	}
}

// Assessment response handler
const submitAssessmentResponse = async (response) => {
	try {
		// Clear text response if it was used
		assessmentTextResponse.value = "";

		// Add user's response to chat
		addOllamaMessage({
			id: `user_assessment_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
			text: `${t('assessment.responsePrefix', 'Response')}: ${response}`,
			sender: "user",
			timestamp: new Date(),
		});

		// Add loading indicator for next question
		const loadingMessageId = `ai_loading_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
		addOllamaMessage({
			id: loadingMessageId,
			text: t('ui.processing', 'Processing your response...'),
			sender: "ai",
			timestamp: new Date(),
			isStreaming: true,
		});

		await scrollToBottom();

		// Continue assessment with the response
		await continueAssessment(response);

		await scrollToBottom();
	} catch (error) {
		console.error("Error submitting assessment response:", error);
	}
};

// Enhanced UI Methods
const getContextualPlaceholder = () => {
	if (conversationMode.value === 'guided' && isAssessmentActive.value) {
		return t('input.assessmentPlaceholder', 'Share your thoughts about this question...');
	}
	if (selectedEmotion.value) {
		return t('input.emotionPlaceholder', `Tell me more about feeling ${selectedEmotion.value}...`);
	}
	if (currentMode.value === 'help') {
		return t('input.helpPlaceholder', 'How are you feeling today? I\'m here to listen...');
	}
	return t('input.placeholder', 'Type your message here...');
};

const handleInputChange = (event) => {
	detectEmotion(event);
	analyzeRealTimeFeedback(event.target.value);
};

const analyzeRealTimeFeedback = (text) => {
	if (!showRealTimeFeedback.value || !text.trim()) {
		isTypingPositive.value = false;
		isTypingNegative.value = false;
		potentialCrisisDetected.value = false;
		return;
	}

	// Simple sentiment analysis
	const positiveWords = ['happy', 'good', 'better', 'grateful', 'thankful', 'hopeful', 'baik', 'senang', 'syukur'];
	const negativeWords = ['sad', 'depressed', 'anxious', 'worried', 'scared', 'sedih', 'cemas', 'takut', 'depresi'];
	const crisisWords = ['suicide', 'kill myself', 'end it all', 'bunuh diri', 'mengakhiri hidup'];

	const lowerText = text.toLowerCase();

	potentialCrisisDetected.value = crisisWords.some(word => lowerText.includes(word));
	isTypingPositive.value = positiveWords.some(word => lowerText.includes(word)) && !potentialCrisisDetected.value;
	isTypingNegative.value = negativeWords.some(word => lowerText.includes(word)) && !potentialCrisisDetected.value;

	// Show empathy validation for positive expressions
	if (isTypingPositive.value) {
		showEmpathyValidation.value = true;
		setTimeout(() => {
			showEmpathyValidation.value = false;
		}, 3000);
	}
};

const toggleEmotionWheel = () => {
	showEmotionWheel.value = !showEmotionWheel.value;
};

const selectEmotion = (emotion) => {
	selectedEmotion.value = emotion;
	showEmotionWheel.value = false;
	showQuickResponses.value = true;
};

const selectQuickResponse = (response) => {
	currentMessage.value = response;
	showQuickResponses.value = false;
	sendMessage();
};

const toggleConversationMode = () => {
	conversationMode.value = conversationMode.value === 'guided' ? 'free' : 'guided';
	if (conversationMode.value === 'free' && isAssessmentActive.value) {
		assessmentPaused.value = true;
	}
};

const pauseAssessment = () => {
	assessmentPaused.value = true;
};

const resumeAssessment = () => {
	assessmentPaused.value = false;
	conversationMode.value = 'guided';
};

const navigateBack = () => {
	if (canNavigateBack.value && ollamaMessages.value.length > 0) {
		// Remove last AI message to go back to previous question
		const lastAiMessageIndex = ollamaMessages.value.map((msg, index) => ({ ...msg, index })).reverse().find(msg => msg.sender === 'ai')?.index;
		if (lastAiMessageIndex !== undefined) {
			ollamaMessages.value.splice(lastAiMessageIndex, 1);
		}
	}
};

const saveProgress = () => {
	// Save current conversation state
	const progressData = {
		messages: ollamaMessages.value,
		assessmentState: {
			isActive: isAssessmentActive.value,
			progress: assessmentProgressPercentage.value,
			paused: assessmentPaused.value
		},
		conversationMode: conversationMode.value,
		timestamp: new Date().toISOString()
	};

	localStorage.setItem('chatbot_progress', JSON.stringify(progressData));
	alert(t('progress.saved', 'Progress saved successfully!'));
};

const exitConversation = () => {
	if (confirm(t('exit.confirm', 'Are you sure you want to exit? Your progress will be saved.'))) {
		saveProgress();
		// Navigate to home or previous page
		navigateToHome();
	}
};

const navigateToHome = () => {
	// Navigate to home page
	navigateToHome('/');
};

// Enhanced Computed Properties
const supportivePrompts = computed(() => {
	if (currentMode.value === 'help') {
		return [
			t('prompts.feelings', 'How are you feeling right now?'),
			t('prompts.today', 'What happened today that brought you here?'),
			t('prompts.support', 'What kind of support do you need most?')
		];
	}
	return [
		t('prompts.general1', 'Tell me more about that...'),
		t('prompts.general2', 'How does that make you feel?'),
		t('prompts.general3', 'What would help you right now?')
	];
});

const emotionOptions = computed(() => [
	{ name: 'happy', emoji: '😊', color: 'text-yellow-500' },
	{ name: 'sad', emoji: '😢', color: 'text-blue-500' },
	{ name: 'angry', emoji: '😠', color: 'text-red-500' },
	{ name: 'anxious', emoji: '😰', color: 'text-purple-500' },
	{ name: 'calm', emoji: '😌', color: 'text-green-500' },
	{ name: 'confused', emoji: '😕', color: 'text-gray-500' },
	{ name: 'excited', emoji: '🤗', color: 'text-orange-500' },
	{ name: 'tired', emoji: '😴', color: 'text-indigo-500' }
]);

const quickResponseOptions = computed(() => {
	if (!selectedEmotion.value) return [];

	const responses = {
		happy: [
			t('responses.happy1', 'I\'m feeling really good today!'),
			t('responses.happy2', 'Something wonderful happened.'),
			t('responses.happy3', 'I want to share my joy.')
		],
		sad: [
			t('responses.sad1', 'I\'ve been feeling down lately.'),
			t('responses.sad2', 'Everything seems overwhelming.'),
			t('responses.sad3', 'I need someone to talk to.')
		],
		anxious: [
			t('responses.anxious1', 'I can\'t stop worrying about things.'),
			t('responses.anxious2', 'My mind is racing with thoughts.'),
			t('responses.anxious3', 'I feel like something bad will happen.')
		]
	};

	return responses[selectedEmotion.value] || [];
});

// Additional Enhanced Methods
const selectSupportivePrompt = (prompt) => {
	currentMessage.value = prompt.text;
	showSupportivePrompts.value = false;
	sendMessage();
};

const toggleSupportivePrompts = () => {
	showSupportivePrompts.value = !showSupportivePrompts.value;
	if (showSupportivePrompts.value) {
		showEmotionWheel.value = false;
		showQuickResponses.value = false;
	}
};

const toggleQuickResponses = () => {
	showQuickResponses.value = !showQuickResponses.value;
	if (showQuickResponses.value) {
		showSupportivePrompts.value = false;
		showEmotionWheel.value = false;
	}
};

const setConversationMode = (mode) => {
	conversationMode.value = mode;
	if (mode === 'free' && isAssessmentActive.value) {
		assessmentPaused.value = true;
	} else if (mode === 'guided' && assessmentPaused.value) {
		resumeAssessment();
	}
};

const goBackInAssessment = () => {
	navigateBack();
};

const exitAssessment = () => {
	if (confirm(t('assessment.exitConfirm', 'Are you sure you want to exit the assessment?'))) {
		saveProgress();
		// Reset assessment state
		assessmentPaused.value = false;
		conversationMode.value = 'free';
	}
};



// Enhanced computed properties for UI state
const assessmentProgress = computed(() => {
	if (!isAssessmentActive.value) return null;

	return {
		isActive: isAssessmentActive.value,
		percentage: assessmentProgressPercentage.value,
		currentQuestion: Math.floor(assessmentProgressPercentage.value / 10) + 1,
		totalQuestions: 10
	};
});

const canGoBack = computed(() => {
	return canNavigateBack.value && ollamaMessages.value.length > 1;
});

onMounted(() => {
	// Focus on input when component mounts
	const textarea = document.querySelector("textarea");
	if (textarea) {
		textarea.addEventListener("input", autoResize);
	}

	// Close menu when clicking outside
	document.addEventListener("click", (e) => {
		if (
			showMenu.value &&
			menuContainer.value &&
			!menuContainer.value.contains(e.target)
		) {
			showMenu.value = false;
		}
	});

	// Initialize speech recognition support check
	if (typeof window !== "undefined") {
		const SpeechRecognition =
			window.SpeechRecognition || window.webkitSpeechRecognition;
		isSpeechSupported.value = !!SpeechRecognition && !!window.speechSynthesis;

		// Track window resize for responsive design
		const handleResize = () => {
			windowWidth.value = window.innerWidth;
		};

		window.addEventListener("resize", handleResize);

		// Cleanup on unmount
		return () => {
			window.removeEventListener("resize", handleResize);
		};
	}
});
</script>

<style scoped>
/* Custom scrollbar */
::-webkit-scrollbar {
	width: 4px;
}

::-webkit-scrollbar-track {
	background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
	background: #c1c1c1;
	border-radius: 2px;
}

::-webkit-scrollbar-thumb:hover {
	background: #a1a1a1;
}

/* Smooth animations */
.animate-bounce {
	animation: bounce 1.4s infinite;
}

@keyframes bounce {
	0%,
	80%,
	100% {
		transform: translateY(0);
	}
	40% {
		transform: translateY(-0.25rem);
	}
}

/* Mobile-specific optimizations */
@media (max-width: 768px) {
	/* Prevent zoom on iOS input focus */
	textarea {
		font-size: 16px;
	}

	/* Touch feedback for buttons */
	button:active {
		transform: scale(0.98);
	}

	/* Smooth scrolling */
	.overflow-y-auto {
		-webkit-overflow-scrolling: touch;
		scroll-behavior: smooth;
	}
}

/* Ensure proper text wrapping */
.break-words {
	word-wrap: break-word;
	overflow-wrap: break-word;
}

/* Ensure navbar visibility */
@media (max-width: 768px) {
	/* Account for navbar height (typically 64px) */
	.bottom-16 {
		bottom: 4rem; /* 64px */
	}

	/* Additional space for navbar */
	.pb-32 {
		padding-bottom: 8rem; /* 128px for input + navbar */
	}
}

@media (min-width: 769px) {
	/* Desktop navbar height adjustment */
	.bottom-16 {
		bottom: 4rem;
	}

	.pb-36 {
		padding-bottom: 9rem; /* 144px for input + navbar */
	}
}

/* Mobile-specific animations */
@media (max-width: 768px) {
	.animate-bounce {
		animation: mobile-bounce 1.2s infinite;
	}
}

@keyframes mobile-bounce {
	0%,
	80%,
	100% {
		transform: translateY(0);
	}
	40% {
		transform: translateY(-0.2rem);
	}
}
</style>
