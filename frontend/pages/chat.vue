<template>
	<div class="chat-page h-full flex flex-col min-h-0">
		<!-- Welcome Message (shown when no messages) -->
		<ClientOnly>
			<div v-if="!hasMessages" class="flex-1 flex items-center justify-center p-4">
				<div class="text-center max-w-sm sm:max-w-md mx-auto">
					<div
						class="w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4 sm:mb-6 shadow-lg"
					>
						<Heart class="w-8 h-8 sm:w-10 sm:h-10 text-white" />
					</div>

					<h2 class="text-xl sm:text-2xl font-semibold text-gray-900 dark:text-white mb-2 sm:mb-3">
						{{ $t("chat.welcome.title", "Welcome to Your Safe Space") }}
					</h2>

					<p class="text-sm sm:text-base text-gray-600 dark:text-gray-300 leading-relaxed">
						{{
							$t(
								"chat.welcome.subtitle",
								"I'm here to listen and support you. How are you feeling today?"
							)
						}}
					</p>
				</div>
			</div>
		</ClientOnly>

		<!-- Messages Container -->
		<ClientOnly>
			<div
				v-if="hasMessages"
				ref="messagesContainer"
				class="flex-1 overflow-y-auto space-y-3 sm:space-y-4 p-3 sm:p-4 scroll-smooth min-h-0"
			>
				<TransitionGroup
					name="message"
					tag="div"
					class="space-y-3 sm:space-y-4"
					@enter="onMessageEnter"
					@leave="onMessageLeave"
				>
					<MessageBubble
						v-for="(message, index) in messages"
						:key="message.id"
						:message="message"
						:index="index"
						@like="likeMessage"
						@copy="copyMessage"
						@typing-complete="onTypingComplete"
						@assessment-answer="handleAssessmentAnswer"
						@assessment-skip="handleAssessmentSkip"
					/>
				</TransitionGroup>

				<!-- Typing Indicator - only show if no streaming message exists -->
				<div v-if="isTyping && !hasStreamingMessage" class="flex justify-start">
					<div class="flex items-start space-x-2">
						<div
							class="w-7 h-7 sm:w-8 sm:h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg"
						>
							<Bot class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" />
						</div>
						<div
							class="bg-white dark:bg-gray-700 rounded-xl sm:rounded-2xl rounded-tl-md p-3 sm:p-4 shadow-sm border border-gray-200 dark:border-gray-600"
						>
							<TypingIndicator />
						</div>
					</div>
				</div>
			</div>
		</ClientOnly>

		<!-- Assessment Progress Indicator -->
		<ClientOnly>
			<div v-if="assessmentProgress.isActive" class="px-3 sm:px-4 py-2 sm:py-3 flex-shrink-0">
				<div class="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-3 border border-blue-200 dark:border-blue-700">
					<div class="flex items-center justify-between mb-2">
						<div class="flex items-center space-x-2">
							<div class="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
								<ClipboardCheck class="w-3 h-3 text-white" />
							</div>
							<span class="text-sm font-medium text-blue-800 dark:text-blue-200">
								{{ $t('assessment.progress', 'Assessment in Progress') }}
							</span>
						</div>
						<button
							@click="handleCancelAssessment"
							class="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200"
						>
							{{ $t('assessment.cancel', 'Cancel') }}
						</button>
					</div>
					<div class="flex items-center justify-between text-xs text-blue-600 dark:text-blue-300 mb-1">
						<span>{{ $t('assessment.question', 'Question') }} {{ assessmentProgress.currentStep }}</span>
						<span>{{ assessmentProgress.totalQuestions }} {{ $t('assessment.total', 'total') }}</span>
					</div>
					<div class="w-full bg-blue-200 dark:bg-blue-800 rounded-full h-1.5">
						<div
							class="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
							:style="{ width: `${(assessmentProgress.currentStep / assessmentProgress.totalQuestions) * 100}%` }"
						></div>
					</div>
				</div>
			</div>
		</ClientOnly>

		<!-- Quick Replies -->
		<ClientOnly>
			<div v-if="quickReplies.length > 0 && !isTyping && !assessmentProgress.isActive" class="px-3 sm:px-4 py-2 sm:py-3 flex-shrink-0">
				<QuickReplies :replies="quickReplies" @select="selectQuickReply" />
			</div>
		</ClientOnly>


		<!-- Input Area -->
		<div
			class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-t border-gray-200/50 dark:border-gray-700/50 p-3 sm:p-4 flex-shrink-0"
		>
			<div class="max-w-4xl mx-auto">
				<div class="flex items-end space-x-2 sm:space-x-3">
					<!-- Text Input -->
					<div class="flex-1 relative">
						<Textarea
							ref="messageInput"
							v-model="currentMessage"
							:placeholder="
								$t('chat.input.placeholder', 'Share what\'s on your mind...')
							"
							class="min-h-[44px] sm:min-h-[48px] max-h-24 sm:max-h-32 resize-none pr-10 sm:pr-12 rounded-xl sm:rounded-2xl border-gray-300 dark:border-gray-600 focus:border-blue-500 dark:focus:border-blue-400 transition-colors text-sm sm:text-base"
							@keydown.enter.prevent="handleEnterKey"
							@input="handleInput"
							@focus="onInputFocus"
							@blur="onInputBlur"
							:disabled="isSending"
						/>

						<!-- Emoji Button -->
						<Button
							variant="ghost"
							size="sm"
							@click="toggleEmojiPicker"
							class="absolute right-1.5 sm:right-2 bottom-1.5 sm:bottom-2 h-7 w-7 sm:h-8 sm:w-8 p-0 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
						>
							<Smile class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
						</Button>
					</div>

					<!-- Send Button -->
					<Button
						@click="sendMessage"
						:disabled="!currentMessage.trim() || isSending"
						class="h-11 w-11 sm:h-12 sm:w-12 rounded-full p-0 transition-all duration-200 shadow-lg flex-shrink-0"
						:class="{
							'scale-110 shadow-xl': currentMessage.trim() && !isSending,
							'opacity-50': !currentMessage.trim() || isSending,
						}"
					>
						<Send v-if="!isSending" class="w-4 h-4 sm:w-5 sm:h-5" />
						<Loader2 v-else class="w-4 h-4 sm:w-5 sm:h-5 animate-spin" />
					</Button>
				</div>
			</div>
		</div>

		<!-- Crisis Alert Modal -->
		<ClientOnly>
			<div
				v-if="showCrisisAlert"
				class="fixed inset-0 bg-red-900/90 backdrop-blur-sm flex items-center justify-center z-50 p-3 sm:p-4"
			>
				<div
					class="bg-white dark:bg-gray-800 rounded-xl sm:rounded-2xl shadow-2xl max-w-sm sm:max-w-md w-full p-4 sm:p-6 max-h-[90vh] overflow-y-auto"
				>
					<div class="text-center mb-4 sm:mb-6">
						<div
							class="w-12 h-12 sm:w-16 sm:h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-3 sm:mb-4"
						>
							<AlertTriangle class="w-6 h-6 sm:w-8 sm:h-8 text-red-600 dark:text-red-400" />
						</div>
						<h3 class="text-lg sm:text-xl font-bold text-gray-900 dark:text-white mb-2">
							{{ $t("crisis.title", "We're Here to Help") }}
						</h3>
						<p class="text-sm sm:text-base text-gray-600 dark:text-gray-300">
							{{
								$t(
									"crisis.message",
									"It sounds like you might be going through a difficult time. You're not alone."
								)
							}}
						</p>
					</div>

					<div class="space-y-2 sm:space-y-3">
						<Button
							variant="destructive"
							size="lg"
							class="w-full justify-start text-sm sm:text-base"
							@click="callCrisisHotline"
						>
							<Phone class="w-4 h-4 sm:w-5 sm:h-5 mr-2 sm:mr-3" />
							{{ $t("crisis.call", "Call Crisis Hotline") }}
							<span class="ml-auto text-xs sm:text-sm opacity-75">24/7</span>
						</Button>

						<Button
							variant="outline"
							size="lg"
							class="w-full justify-start text-sm sm:text-base"
							@click="continueChat"
						>
							<MessageCircle class="w-4 h-4 sm:w-5 sm:h-5 mr-2 sm:mr-3" />
							{{ $t("crisis.continue", "Continue Chat") }}
						</Button>
					</div>
				</div>
			</div>
		</ClientOnly>
	</div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from "vue";
import { useI18n } from "vue-i18n";
import { Button } from "@/components/ui/button";
import Textarea from "@/components/ui/textarea/Textarea.vue";
import {
	Heart,
	Bot,
	Send,
	Smile,
	Loader2,
	AlertTriangle,
	Phone,
	MessageCircle,
	ClipboardCheck,
} from "lucide-vue-next";

// Import our custom components
import MessageBubble from "@/components/animations/MessageBubble.vue";
import QuickReplies from "@/components/animations/QuickReplies.vue";
import TypingIndicator from "@/components/animations/TypingIndicator.vue";

// Import chat composable
import { useOllamaChat } from "@/composables/useOllamaChat";

// Set layout
definePageMeta({
	layout: "chat-layout",
});

// I18n
const { t, locale } = useI18n();

// Define interfaces for type safety
interface Message {
	id: string;
	text: string;
	sender: "user" | "ai";
	timestamp: Date;
	status?: "sending" | "sent" | "delivered";
	liked?: boolean;
	isStreaming?: boolean;
	error?: string;
	sentiment?: any;
	isCrisis?: boolean;
	problemCategory?: string;
	suggestions?: any;
	assessmentQuestions?: any;
	showAssessmentTransition?: boolean;
	contextAnalysis?: any;
	assessmentProgress?: {
		current: number;
		total: number;
	};
	// Assessment suggestion fields
	isAssessmentSuggestion?: boolean;
	suggestedCategory?: string;
	subCategoryId?: string;
}

interface QuickReply {
	id: string;
	text: string;
	category?: string;
}

// Chat composable
const {
	messages: ollamaMessages,
	sendMessage: sendOllamaMessage,
	sendMessageStream,
	sendMessageWithAssessment,
	isProcessing: ollamaIsProcessing,
	isStreaming: ollamaIsStreaming,
	error: ollamaError,
	isConnected,
	sessionId,
	addMessage,
	clearMessages,
	hasMessages,
	searchMentalHealthContext,
	getTherapeuticSuggestions,
	// Assessment methods
	startAssessment,
	submitAssessmentAnswer,
	getAssessmentStatus,
	cancelAssessment,
	assessmentProgress,
} = useOllamaChat();

// Convert ollama messages to our Message interface
const messages = computed((): Message[] => {
	return ollamaMessages.value.map((msg: any) => ({
		id: msg.id,
		text: msg.text,
		sender: msg.sender,
		timestamp:
			typeof msg.timestamp === "string"
				? new Date(msg.timestamp)
				: msg.timestamp,
		status: msg.status || "sent",
		liked: msg.liked || false,
		isStreaming: msg.isStreaming || false,
		error: msg.error,
		// Include sentiment analysis data
		sentiment: msg.sentiment,
		isCrisis: msg.isCrisis,
		problemCategory: msg.problemCategory,
		suggestions: msg.suggestions,
		assessmentQuestions: msg.assessmentQuestions,
		showAssessmentTransition: msg.showAssessmentTransition,
		contextAnalysis: msg.contextAnalysis,
		assessmentProgress: msg.assessmentProgress,
		// Assessment suggestion fields
		isAssessmentSuggestion: msg.isAssessmentSuggestion,
		suggestedCategory: msg.suggestedCategory,
		subCategoryId: msg.subCategoryId,
	}));
});

// State
const currentMessage = ref("");
const isSending = ref(false);
const isTyping = computed(
	() => ollamaIsProcessing.value || ollamaIsStreaming.value
);

// Check if there's already a streaming message to avoid duplicate typing indicators
const hasStreamingMessage = computed(() => {
	return ollamaMessages.value.some((msg: any) => msg.isStreaming === true);
});
const showCrisisAlert = ref(false);
const messagesContainer = ref<HTMLElement>();
const messageInput = ref<any>();


// Quick replies - make them reactive to language changes
const quickReplies = computed((): QuickReply[] => [
	{
		id: "1",
		text: t("quickReplies.feeling", "I'm feeling anxious"),
		category: "emotion",
	},
	{
		id: "2",
		text: t("quickReplies.help", "I need coping strategies"),
		category: "help",
	},
	{
		id: "3",
		text: t("quickReplies.sleep", "I'm having trouble sleeping"),
		category: "issue",
	},
	{
		id: "4",
		text: t("quickReplies.assessment", "I'd like to do an assessment"),
		category: "assessment",
	},
	{
		id: "5",
		text: t("quickReplies.stress", "I'm feeling stressed"),
		category: "emotion",
	},
	{
		id: "6",
		text: t("quickReplies.depression", "I think I might be depressed"),
		category: "emotion",
	},
]);

// Crisis keywords
const crisisKeywords = [
	"bunuh diri",
	"suicide",
	"mati",
	"death",
	"tidak ada harapan",
	"no hope",
	"putus asa",
];

// Methods
const sendMessage = async (): Promise<void> => {
	if (!currentMessage.value.trim() || isSending.value) return;

	const messageText = currentMessage.value.trim();

	// Check for crisis keywords
	if (checkForCrisis(messageText)) {
		showCrisisAlert.value = true;
	}

	// Create user message object
	const userMessage: Message = {
		id: `user_${Date.now()}`,
		text: messageText,
		sender: "user",
		timestamp: new Date(),
		status: "sending",
		liked: false,
		error: undefined,
	};

	addMessage(userMessage);
	const messageTextToSend = currentMessage.value;
	currentMessage.value = "";
	isSending.value = true;

	await nextTick();
	scrollToBottom();

	try {
		// Create AI message placeholder for streaming
		const aiMessageId = `ai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
		const aiMessage = {
			id: aiMessageId,
			text: "",
			sender: "ai" as const,
			timestamp: new Date(),
			isStreaming: true,
		};
		addMessage(aiMessage);
		await scrollToBottom();

		// Use enhanced streaming with assessment integration
		await sendMessageWithAssessment(
			messageTextToSend,
			{
				sessionId: sessionId.value,
				preferredLanguage: locale.value,
			},
			(chunk) => {
				// Update the AI message with streaming content
				console.log('📝 Received chunk:', chunk, 'Length:', chunk.length);
				const messageIndex = ollamaMessages.value.findIndex(msg => msg.id === aiMessageId);
				if (messageIndex !== -1) {
					// Ensure we're properly appending, not replacing
					const currentText = ollamaMessages.value[messageIndex].text || '';
					ollamaMessages.value[messageIndex].text = currentText + chunk;
					console.log('📝 Updated text:', ollamaMessages.value[messageIndex].text);
					scrollToBottom();
				}
			},
			(finalResponse) => {
				// Update the AI message with final data
				const messageIndex = ollamaMessages.value.findIndex(msg => msg.id === aiMessageId);
				if (messageIndex !== -1) {
					ollamaMessages.value[messageIndex].isStreaming = false;
					if (finalResponse) {
						// Only set message text if no chunks were received
						if (finalResponse.message && ollamaMessages.value[messageIndex].text.length === 0) {
							ollamaMessages.value[messageIndex].text = finalResponse.message;
						}
						// Set metadata
						ollamaMessages.value[messageIndex].sentiment = finalResponse.sentiment;
						ollamaMessages.value[messageIndex].isCrisis = finalResponse.isCrisis;
						ollamaMessages.value[messageIndex].problemCategory = finalResponse.problemCategory;
						ollamaMessages.value[messageIndex].suggestions = finalResponse.suggestions;
						ollamaMessages.value[messageIndex].assessmentQuestions = finalResponse.assessmentQuestions;
						ollamaMessages.value[messageIndex].showAssessmentTransition = finalResponse.showAssessmentTransition;
						ollamaMessages.value[messageIndex].contextAnalysis = finalResponse.contextAnalysis;
						ollamaMessages.value[messageIndex].assessmentProgress = finalResponse.assessmentProgress;
						// Assessment suggestion fields
						ollamaMessages.value[messageIndex].isAssessmentSuggestion = finalResponse.isAssessmentSuggestion;
						ollamaMessages.value[messageIndex].suggestedCategory = finalResponse.suggestedCategory;
						ollamaMessages.value[messageIndex].subCategoryId = finalResponse.subCategoryId;

						console.log('📊 SSE data processed:', finalResponse);

						// Handle assessment suggestion
						if (finalResponse.isAssessmentSuggestion && finalResponse.suggestedCategory) {
							console.log('🎯 Assessment suggestion detected:', {
								category: finalResponse.suggestedCategory,
								subCategoryId: finalResponse.subCategoryId
							});

							// Automatically start assessment after a short delay
							setTimeout(async () => {
								try {
									const assessmentResult = await startAssessment(
										finalResponse.suggestedCategory,
										finalResponse.subCategoryId
									);

									if (assessmentResult.type === 'assessment_question') {
										console.log('🔍 Assessment result question structure:', {
											question: assessmentResult.question,
											questionKeys: assessmentResult.question ? Object.keys(assessmentResult.question) : 'No question object',
											questionId: assessmentResult.question?.question_id,
											progress: assessmentResult.progress
										});

										// Add assessment question message
										const assessmentMessage: Message = {
											id: `ai_assessment_${Date.now()}`,
											text: "Let's start with a few questions to better understand your situation:",
											sender: "ai",
											timestamp: new Date(),
											assessmentQuestions: [assessmentResult.question],
											assessmentProgress: {
												current: assessmentResult.progress?.current || 1,
												total: assessmentResult.progress?.total || 10,
											},
										};
										addMessage(assessmentMessage);
										await scrollToBottom();
									}
								} catch (error) {
									console.error('❌ Error starting assessment:', error);
								}
							}, 2000); // 2 second delay to let user read the suggestion
						}
					}
					scrollToBottom();
				}
			},
			(assessmentQuestion) => {
				// Handle assessment question
				console.log('📝 Assessment question received:', assessmentQuestion);
				console.log('🔍 Question object structure:', {
					question: assessmentQuestion.question,
					questionKeys: assessmentQuestion.question ? Object.keys(assessmentQuestion.question) : 'No question object',
					questionId: assessmentQuestion.question?.question_id,
					progress: assessmentQuestion.progress
				});

				const messageIndex = ollamaMessages.value.findIndex(msg => msg.id === aiMessageId);
				if (messageIndex !== -1) {
					ollamaMessages.value[messageIndex].assessmentQuestions = [assessmentQuestion.question];
					ollamaMessages.value[messageIndex].assessmentProgress = assessmentQuestion.progress;
					scrollToBottom();
				}
			}
		);

		// Update user message status
		const messageToUpdate = ollamaMessages.value.find(
			(m: any) => m.id === userMessage.id
		);
		if (messageToUpdate) {
			Object.assign(messageToUpdate, { status: "delivered" });
		}
	} catch (error) {
		console.error("Error sending message:", error);

		// Update message with error
		const messageToUpdate = ollamaMessages.value.find(
			(m: any) => m.id === userMessage.id
		);
		if (messageToUpdate) {
			Object.assign(messageToUpdate, {
				status: "delivered",
				error: "Failed to send message",
			});
		}
	} finally {
		isSending.value = false;
	}
};

const selectQuickReply = async (reply: QuickReply): Promise<void> => {
	// Handle assessment quick reply specially
	if (reply.category === "assessment") {
		try {
			console.log('🎯 Assessment quick reply selected');

			// Add user message
			const userMessage: Message = {
				id: `user_${Date.now()}`,
				text: reply.text,
				sender: "user",
				timestamp: new Date(),
				status: "sent",
				liked: false,
			};
			addMessage(userMessage);
			await scrollToBottom();

			// Start assessment directly
			const assessmentResult = await startAssessment("Mental Health Assessment");

			if (assessmentResult.type === 'assessment_question') {
				console.log('🔍 Quick reply assessment result question structure:', {
					question: assessmentResult.question,
					questionKeys: assessmentResult.question ? Object.keys(assessmentResult.question) : 'No question object',
					questionId: assessmentResult.question?.question_id,
					progress: assessmentResult.progress
				});

				// Add assessment question message
				const assessmentMessage: Message = {
					id: `ai_assessment_${Date.now()}`,
					text: "I'd be happy to help you with an assessment. Let's start with a few questions:",
					sender: "ai",
					timestamp: new Date(),
					assessmentQuestions: [assessmentResult.question],
					assessmentProgress: {
						current: assessmentResult.progress?.current || 1,
						total: assessmentResult.progress?.total || 10,
					},
				};
				addMessage(assessmentMessage);
				await scrollToBottom();
			} else if (assessmentResult.type === 'error') {
				// Show error message
				const errorMessage: Message = {
					id: `ai_error_${Date.now()}`,
					text: `Sorry, there was an error starting the assessment: ${assessmentResult.message}`,
					sender: "ai",
					timestamp: new Date(),
					error: assessmentResult.message,
				};
				addMessage(errorMessage);
				await scrollToBottom();
			}
		} catch (error) {
			console.error('❌ Error handling assessment quick reply:', error);

			// Fallback to regular message
			currentMessage.value = reply.text;
			sendMessage();
		}
	} else if (reply.category === "emotion") {
		// Handle emotion-based quick replies that might trigger assessment suggestions
		currentMessage.value = reply.text;
		sendMessage();
	} else {
		// Handle other quick replies normally
		currentMessage.value = reply.text;
		sendMessage();
	}
};

const handleEnterKey = (event: KeyboardEvent): void => {
	if (!event.shiftKey) {
		sendMessage();
	}
};

const handleInput = (): void => {
	// Auto-resize textarea
	if (messageInput.value && messageInput.value.$el) {
		const textarea = messageInput.value.$el;
		if (textarea && textarea.style) {
			textarea.style.height = "auto";
			textarea.style.height = `${Math.min(textarea.scrollHeight, 128)}px`;
		}
	} else if (messageInput.value && messageInput.value.style) {
		// Fallback for direct textarea element
		messageInput.value.style.height = "auto";
		messageInput.value.style.height = `${Math.min(
			messageInput.value.scrollHeight,
			128
		)}px`;
	}
};

const checkForCrisis = (message: string): boolean => {
	const lowerMessage = message.toLowerCase();
	return crisisKeywords.some((keyword) => lowerMessage.includes(keyword));
};

const scrollToBottom = async (): Promise<void> => {
	await nextTick();
	if (messagesContainer.value) {
		messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
	}
};

const likeMessage = (messageId: string): void => {
	const message = ollamaMessages.value.find((m: any) => m.id === messageId);
	if (message) {
		(message as any).liked = !((message as any).liked || false);
	}
};

const copyMessage = async (text: string): Promise<void> => {
	try {
		await navigator.clipboard.writeText(text);
		// Could add toast notification here
	} catch (error) {
		console.error("Failed to copy message:", error);
	}
};

const onTypingComplete = (messageId: string): void => {
	// Handle typing completion
	console.log("Typing completed for message:", messageId);
};

const onMessageEnter = (el: Element): void => {
	// Custom enter animation
	scrollToBottom();
};

const onMessageLeave = (el: Element): void => {
	// Custom leave animation
};

const toggleEmojiPicker = (): void => {
	// Implement emoji picker
	console.log("Toggle emoji picker");
};

const callCrisisHotline = (): void => {
	window.open("tel:119", "_self");
};

const continueChat = (): void => {
	showCrisisAlert.value = false;
};


const onInputFocus = (): void => {
	// Handle mobile keyboard appearance
	if (window.innerWidth <= 768) {
		setTimeout(() => {
			scrollToBottom();
		}, 300); // Wait for keyboard animation
	}
};

const onInputBlur = (): void => {
	// Handle mobile keyboard dismissal
	if (window.innerWidth <= 768) {
		setTimeout(() => {
			scrollToBottom();
		}, 300);
	}
};

// Assessment response handlers
const handleAssessmentAnswer = async (questionId: string, answer: any): Promise<void> => {
	try {
		console.log('📝 Submitting assessment answer:', { questionId, answer });

		// Add user's answer as a message
		const userAnswerMessage: Message = {
			id: `user_answer_${Date.now()}`,
			text: `Assessment Answer: ${typeof answer === 'string' ? answer : JSON.stringify(answer)}`,
			sender: "user",
			timestamp: new Date(),
			status: "sent",
			liked: false,
		};
		addMessage(userAnswerMessage);
		await scrollToBottom();

		// Submit the answer to the backend
		const result = await submitAssessmentAnswer(questionId, answer);

		if (result.type === 'assessment_question') {
			// Next question received
			const nextQuestionMessage: Message = {
				id: `ai_question_${Date.now()}`,
				text: result.message || "Here's the next question:",
				sender: "ai",
				timestamp: new Date(),
				assessmentQuestions: [result.question],
				assessmentProgress: {
					current: result.progress?.current || assessmentProgress.value.currentStep,
					total: result.progress?.total || assessmentProgress.value.totalQuestions,
				},
			};
			addMessage(nextQuestionMessage);
		} else if (result.type === 'assessment_complete') {
			// Assessment completed
			const completionMessage: Message = {
				id: `ai_complete_${Date.now()}`,
				text: result.message || "Assessment completed! Here are your results:",
				sender: "ai",
				timestamp: new Date(),
				suggestions: result.recommendations || result.suggestions,
				contextAnalysis: result.analysis,
			};
			addMessage(completionMessage);
		} else if (result.type === 'error') {
			// Error occurred
			const errorMessage: Message = {
				id: `ai_error_${Date.now()}`,
				text: `Sorry, there was an error: ${result.message}`,
				sender: "ai",
				timestamp: new Date(),
				error: result.message,
			};
			addMessage(errorMessage);
		}

		await scrollToBottom();
	} catch (error) {
		console.error('❌ Error handling assessment answer:', error);

		const errorMessage: Message = {
			id: `ai_error_${Date.now()}`,
			text: "Sorry, there was an error processing your answer. Please try again.",
			sender: "ai",
			timestamp: new Date(),
			error: "Failed to process assessment answer",
		};
		addMessage(errorMessage);
		await scrollToBottom();
	}
};

const handleAssessmentSkip = async (questionId: string): Promise<void> => {
	try {
		console.log('⏭️ Skipping assessment question:', questionId);

		// Add skip message
		const skipMessage: Message = {
			id: `user_skip_${Date.now()}`,
			text: "Skipped this question",
			sender: "user",
			timestamp: new Date(),
			status: "sent",
			liked: false,
		};
		addMessage(skipMessage);
		await scrollToBottom();

		// Submit skip to backend (you might want to implement this in the backend)
		// For now, we'll just continue with the next question
		const result = await submitAssessmentAnswer(questionId, "skipped");

		if (result.type === 'assessment_question') {
			const nextQuestionMessage: Message = {
				id: `ai_question_${Date.now()}`,
				text: "Here's the next question:",
				sender: "ai",
				timestamp: new Date(),
				assessmentQuestions: [result.question],
				assessmentProgress: {
					current: result.progress?.current || assessmentProgress.value.currentStep,
					total: result.progress?.total || assessmentProgress.value.totalQuestions,
				},
			};
			addMessage(nextQuestionMessage);
		}

		await scrollToBottom();
	} catch (error) {
		console.error('❌ Error skipping assessment question:', error);
	}
};

// Cancel assessment handler
const handleCancelAssessment = async (): Promise<void> => {
	try {
		console.log('❌ Canceling assessment');

		// Add cancel message
		const cancelMessage: Message = {
			id: `user_cancel_${Date.now()}`,
			text: "Assessment canceled",
			sender: "user",
			timestamp: new Date(),
			status: "sent",
			liked: false,
		};
		addMessage(cancelMessage);

		// Cancel the assessment
		await cancelAssessment();

		// Add confirmation message
		const confirmMessage: Message = {
			id: `ai_cancel_${Date.now()}`,
			text: "Assessment has been canceled. You can start a new assessment anytime by asking me.",
			sender: "ai",
			timestamp: new Date(),
		};
		addMessage(confirmMessage);

		await scrollToBottom();
	} catch (error) {
		console.error('❌ Error canceling assessment:', error);
	}
};

// Lifecycle
onMounted(() => {
	// Initialize with welcome message if no messages
	if (!hasMessages.value) {
		const welcomeMessage: Message = {
			id: "welcome",
			text: t(
				"chat.welcome.ai",
				"Hello! I'm here to support your mental health journey. How are you feeling today?"
			),
			sender: "ai",
			timestamp: new Date(),
			liked: false,
		};
		addMessage(welcomeMessage);
	}

	// Debug: Log assessment progress state
	console.log('🔍 Initial assessment progress:', assessmentProgress.value);
});

// Watch for locale changes to update welcome message if it exists
watch(locale, (newLocale) => {
	const welcomeMessage = ollamaMessages.value.find((msg: any) => msg.id === "welcome");
	if (welcomeMessage) {
		welcomeMessage.text = t(
			"chat.welcome.ai",
			"Hello! I'm here to support your mental health journey. How are you feeling today?"
		);
	}
});

onUnmounted(() => {
	// Cleanup
});
</script>

<style scoped>
.chat-page {
	/* Use full height with proper mobile handling */
	height: 100%;
	min-height: 0;
	/* Handle mobile viewport units */
	height: 100vh;
	height: 100dvh; /* Dynamic viewport height for mobile */
}

/* Mobile-specific adjustments */
@supports (height: 100dvh) {
	.chat-page {
		height: 100dvh;
	}
}

/* Handle iOS Safari viewport issues */
@supports (-webkit-touch-callout: none) {
	.chat-page {
		height: -webkit-fill-available;
	}
}

/* Message transition animations */
.message-enter-active {
	transition: all 0.5s ease-out;
}

.message-leave-active {
	transition: all 0.3s ease-in;
}

.message-enter-from {
	opacity: 0;
	transform: translateY(20px) scale(0.9);
}

.message-leave-to {
	opacity: 0;
	transform: translateY(-20px) scale(0.9);
}

/* Smooth scrolling */
.scroll-smooth {
	scroll-behavior: smooth;
}

/* Custom scrollbar */
.messages-container::-webkit-scrollbar {
	width: 4px;
}

.messages-container::-webkit-scrollbar-track {
	background: transparent;
}

.messages-container::-webkit-scrollbar-thumb {
	background: #cbd5e1;
	border-radius: 2px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
	background: #94a3b8;
}

/* Mobile keyboard handling */
@media (max-width: 768px) {
	.chat-page {
		/* Ensure content doesn't get cut off when keyboard appears */
		min-height: 100vh;
		min-height: 100dvh;
	}

	/* Adjust input area for mobile */
	.chat-page .input-area {
		/* Add safe area padding for mobile */
		padding-bottom: env(safe-area-inset-bottom);
	}
}

/* Respect reduced motion preferences */
@media (prefers-reduced-motion: reduce) {
	.message-enter-active,
	.message-leave-active {
		transition: none;
	}

	.scroll-smooth {
		scroll-behavior: auto;
	}
}

/* Ensure proper flex behavior on mobile */
@media (max-width: 640px) {
	.chat-page {
		/* Prevent content from being cut off */
		overflow: hidden;
	}
}
</style>
