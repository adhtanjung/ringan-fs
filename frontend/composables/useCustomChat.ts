import { ref, onUnmounted } from "vue";
import { marked } from "marked";

export const useCustomChat = () => {
	const config = useRuntimeConfig();
	const isProcessing = ref(false);
	const error = ref<string | null>(null);
	const isConnected = ref(false);
	const isStreaming = ref(false);

	// WebSocket instance
	let ws: WebSocket | null = null;
	let sessionId = ref("");

	// Configure marked options
	marked.setOptions({
		breaks: true, // Convert line breaks to <br>
		gfm: true, // GitHub Flavored Markdown
	});

	const convertMarkdownToHtml = (text: string) => {
		return marked(text);
	};

	// Generate session ID
	const generateSessionId = () => {
		return (
			"session_" + Date.now() + "_" + Math.random().toString(36).substr(2, 9)
		);
	};

	// HTTP API Chat (Non-streaming)
	const generateResponse = async (
		messages: { role: string; content: string }[]
	) => {
		isProcessing.value = true;
		error.value = null;

		try {
			// Get auth token from localStorage
			const token =
				localStorage.getItem("auth_token") || config.public.customChatApiKey;

			const response = await fetch(config.public.customChatApiUrl, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${token}`,
				},
				body: JSON.stringify({
					messages: [
						{
							role: "system",
							content: `Kamu adalah Ringan AI, asisten kesehatan mental yang ramah dan empatik. Kamu selalu merespons dengan bahasa yang santai dan mudah dipahami, bertata kata seperi halnya seorang psikolog. Kamu fokus pada menganalisa permasalahan pengguna dan memberika saran saran yang membantu untuk kesehatan mental.

              Gunakan format markdown untuk merapikan responsmu:
              - Gunakan **bold** untuk penekanan
              - Gunakan *italic* untuk kata-kata penting
              - Gunakan list dengan bullet points (-) atau nomor (1. 2. 3.)
              - Gunakan > untuk kutipan
              - Gunakan \`\`\` untuk kode atau contoh
              - Gunakan --- untuk pemisah
              - Gunakan emoji yang sesuai dengan konteks`,
						},
						...messages,
					],
					stream: false, // Set to false for non-streaming
				}),
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();

			// Adapt response format based on your API structure
			// Assuming your API returns { message: "response text" } or similar
			const content =
				data.message ||
				data.response ||
				data.content ||
				data.choices?.[0]?.message?.content;

			if (!content) {
				throw new Error("No content in response");
			}

			return convertMarkdownToHtml(content);
		} catch (err) {
			console.error("Chat API Error:", err);
			error.value = err instanceof Error ? err.message : "An error occurred";
			return null;
		} finally {
			isProcessing.value = false;
		}
	};

	// WebSocket Chat (Streaming)
	const connectWebSocket = (
		onMessage?: (message: string) => void,
		onComplete?: () => void
	) => {
		if (ws && ws.readyState === WebSocket.OPEN) {
			return; // Already connected
		}

		// Generate session ID if not exists
		if (!sessionId.value) {
			sessionId.value = generateSessionId();
		}

		const token =
			localStorage.getItem("auth_token") || config.public.customChatApiKey;
		const wsUrl = config.public.customChatWsUrl;

		console.log("Attempting to connect to WebSocket:", wsUrl);

		try {
			ws = new WebSocket(wsUrl);

			ws.onopen = () => {
				isConnected.value = true;
				error.value = null;
				console.log("WebSocket connected successfully to:", wsUrl);
			};

			ws.onmessage = (event) => {
				try {
					console.log("WebSocket message received:", event.data);
					const data = JSON.parse(event.data);

					// Handle different message types based on your WebSocket API
					if (data.type === "chunk") {
						const content = data.content;
						if (content && onMessage) {
							onMessage(content);
						}
					} else if (data.type === "complete") {
						isStreaming.value = false;
						if (onComplete) {
							onComplete();
						}
					} else if (data.type === "error") {
						error.value = data.message || "WebSocket error occurred";
						isStreaming.value = false;
					}
				} catch (err) {
					console.error("Error parsing WebSocket message:", err);
				}
			};

			ws.onerror = (event) => {
				console.error("WebSocket error occurred:", event);
				error.value = "WebSocket connection error - server may not be running";
				isConnected.value = false;
				isStreaming.value = false;
			};

			ws.onclose = (event) => {
				isConnected.value = false;
				isStreaming.value = false;
				console.log(
					"WebSocket disconnected. Code:",
					event.code,
					"Reason:",
					event.reason
				);

				// Provide more specific error messages based on close codes
				if (event.code === 1006) {
					error.value =
						"WebSocket server is not reachable. Please ensure your custom chat server is running on localhost:8000";
				} else if (event.code === 1002) {
					error.value = "WebSocket protocol error";
				} else if (event.code === 1003) {
					error.value = "WebSocket data type error";
				} else if (event.code === 1011) {
					error.value = "WebSocket server error";
				} else if (event.code !== 1000) {
					error.value = `WebSocket closed unexpectedly (Code: ${event.code})`;
				}
			};
		} catch (err) {
			console.error("Failed to create WebSocket connection:", err);
			error.value =
				"Failed to connect to chat service - please check if the server is running";
		}
	};

	// Send message via WebSocket
	const sendWebSocketMessage = (
		content: string,
		messages: { role: string; content: string }[] = []
	) => {
		if (!ws || ws.readyState !== WebSocket.OPEN) {
			error.value = "WebSocket not connected";
			return false;
		}

		try {
			isStreaming.value = true;
			error.value = null;

			// Send message with context
			const messageData = {
				type: "chat_message",
				content: content,
				context: messages.length > 0 ? messages : undefined,
				session_id: sessionId.value,
			};

			ws.send(JSON.stringify(messageData));
			return true;
		} catch (err) {
			console.error("Error sending WebSocket message:", err);
			error.value = "Failed to send message";
			isStreaming.value = false;
			return false;
		}
	};

	// Streaming response handler
	const generateStreamingResponse = async (
		messages: { role: string; content: string }[],
		onChunk?: (chunk: string) => void,
		onComplete?: (fullResponse: string) => void
	) => {
		return new Promise<string>(async (resolve, reject) => {
			let fullResponse = "";

			const handleMessage = (chunk: string) => {
				fullResponse += chunk;
				if (onChunk) {
					onChunk(chunk);
				}
			};

			const handleComplete = () => {
				const htmlContent = convertMarkdownToHtml(fullResponse);
				if (onComplete) {
					onComplete(htmlContent);
				}
				resolve(htmlContent);
			};

			// Try WebSocket first
			if (!isConnected.value) {
				connectWebSocket(handleMessage, handleComplete);

				// Wait for connection then send message
				const checkConnection = setInterval(() => {
					if (isConnected.value) {
						clearInterval(checkConnection);
						const userMessage = messages[messages.length - 1]?.content || "";
						if (!sendWebSocketMessage(userMessage, messages.slice(0, -1))) {
							reject(new Error("Failed to send message"));
						}
					}
				}, 100);

				// Timeout after 3 seconds, then fallback to HTTP
				setTimeout(async () => {
					clearInterval(checkConnection);
					if (!isConnected.value) {
						console.log(
							"WebSocket connection failed, falling back to HTTP API"
						);
						try {
							// Fallback to HTTP API
							const response = await generateResponse(messages);
							if (response) {
								if (onComplete) {
									onComplete(response);
								}
								resolve(response);
							} else {
								reject(new Error("Both WebSocket and HTTP API failed"));
							}
						} catch (err) {
							reject(err);
						}
					}
				}, 3000);
			} else {
				// Already connected, send message directly
				const userMessage = messages[messages.length - 1]?.content || "";
				if (!sendWebSocketMessage(userMessage, messages.slice(0, -1))) {
					// If WebSocket send fails, fallback to HTTP
					console.log("WebSocket send failed, falling back to HTTP API");
					try {
						const response = await generateResponse(messages);
						if (response) {
							if (onComplete) {
								onComplete(response);
							}
							resolve(response);
						} else {
							reject(new Error("Both WebSocket and HTTP API failed"));
						}
					} catch (err) {
						reject(err);
					}
				}
			}
		});
	};

	// Disconnect WebSocket
	const disconnectWebSocket = () => {
		if (ws) {
			ws.close();
			ws = null;
		}
		isConnected.value = false;
		isStreaming.value = false;
	};

	// Cleanup on unmount
	onUnmounted(() => {
		disconnectWebSocket();
	});

	return {
		// HTTP API
		generateResponse,

		// WebSocket API
		connectWebSocket,
		sendWebSocketMessage,
		generateStreamingResponse,
		disconnectWebSocket,

		// State
		isProcessing,
		error,
		isConnected,
		isStreaming,
		sessionId,

		// Utilities
		convertMarkdownToHtml,
	};
};
