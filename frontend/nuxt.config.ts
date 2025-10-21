// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
	compatibilityDate: "2024-11-01",
	devtools: { enabled: true },
	ssr: true,
	modules: [
		"@nuxt/image",
		"@nuxt/fonts",
		"@nuxtjs/tailwindcss",
		"shadcn-nuxt",
		"@pinia/nuxt",
		"@nuxtjs/i18n",
		"@vueuse/motion/nuxt",
	],
	fonts: {
		families: [
			{
				name: "Plus Jakarta Sans",
				provider: "google",
				weights: ["200", "300", "400", "500", "600", "700", "800"],
				styles: ["normal", "italic"],
			},
		],
	},
	shadcn: {
		/**
		 * Prefix for all the imported component
		 */
		prefix: "",
		/**
		 * Directory that the component lives in.
		 * @default "./components/ui"
		 */
		componentDir: "./components/ui",
	},
	vite: {
		server: {
			hmr: true,
			allowedHosts: [
				"localhost",
				"127.0.0.1",
				"4145-182-253-57-219.ngrok-free.app",
				".ngrok-free.app", // Allow any ngrok subdomain
			],
		},
		build: {
			cssCodeSplit: true,
			emptyOutDir: true,
		},
	},
	runtimeConfig: {
		// Private keys (server-side only)
		apiSecret: process.env.API_SECRET || "",

		// Public keys (exposed to client)
		public: {
			apiBaseUrl: process.env.API_BASE_URL || "http://localhost:5554/",
			appEnvironment: process.env.APP_ENV || "development",
			isDev: process.env.APP_IS_DEV === "true", // Custom flag for development mode

			// Backend API Configuration
			backendApiUrl:
				process.env.NUXT_PUBLIC_BACKEND_API_URL ||
				"http://localhost:8000/api/v1",
			adminApiUrl:
				process.env.NUXT_PUBLIC_ADMIN_API_URL ||
				"http://localhost:8000/api/v1/admin",
			vectorApiUrl:
				process.env.NUXT_PUBLIC_VECTOR_API_URL ||
				"http://localhost:8000/api/v1/vector",

			// Python Backend Configuration (Ollama)
			customChatApiUrl:
				process.env.NUXT_PUBLIC_CUSTOM_CHAT_API_URL ||
				"http://localhost:8000/api/v1/chat",
			customChatWsUrl:
				process.env.NUXT_PUBLIC_CUSTOM_CHAT_WS_URL ||
				"ws://localhost:8000/api/v1/chat/ws",
			customChatApiKey:
				process.env.NUXT_PUBLIC_CUSTOM_CHAT_API_KEY || "your_jwt_token",

			// OpenAI Configuration (Fallback)
			openaiApiKey: process.env.OPENAI_API_KEY || "", // OpenAI API key
			openaiTemperature: parseFloat(process.env.OPENAI_TEMPERATURE || "0.7"), // OpenAI temperature
			openaiMaxTokens: parseInt(process.env.OPENAI_MAX_TOKENS || "200"), // OpenAI max tokens

			// Demo Configuration
			demoMaxChats: parseInt(process.env.DEMO_MAX_CHATS || "10"), // Maximum chats in demo session

			// ElevenLabs Configuration
			elevenlabsApiKey: process.env.ELEVENLABS_API_KEY || "", // ElevenLabs API key
			elevenlabsVoiceId:
				process.env.ELEVENLABS_VOICE_ID || "iWydkXKoiVtvdn4vLKp9", // ElevenLabs voice ID (default: Adam)
			elevenlabsModel: process.env.ELEVENLABS_MODEL || "eleven_flash_v2_5", // ElevenLabs model
		},
	},
	app: {
		head: {
			meta: [
				{ name: "viewport", content: "width=device-width, initial-scale=1" },
			],
			link: [
				{ rel: "icon", type: "image/x-icon", href: "/favicon.ico" },
				{ rel: "preconnect", href: "https://fonts.googleapis.com" },
				{
					rel: "preconnect",
					href: "https://fonts.gstatic.com",
					crossorigin: "",
				},
				{
					rel: "stylesheet",
					href: "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,200;0,300;0,400;0,500;0,600;0,700;0,800;1,200;1,300;1,400;1,500;1,600;1,700;1,800&display=swap",
				},
			],
		},
	},
	imports: {
		dirs: ["stores", "composables", "utils"],
	},
	i18n: {
		locales: [
			{
				code: "en",
				name: "English",
				file: "en.json",
			},
			{
				code: "id",
				name: "Bahasa Indonesia",
				file: "id.json",
			},
		],
		defaultLocale: "id",
		langDir: "locales",
		strategy: "no_prefix",
		detectBrowserLanguage: {
			useCookie: true,
			cookieKey: "i18n_redirected",
			redirectOn: "root",
			fallbackLocale: "id",
		},
		compilation: {
			strictMessage: false,
			escapeHtml: true,
		},
		bundle: {
			compositionOnly: true,
			runtimeOnly: false,
			fullInstall: true,
			dropMessageCompiler: false,
		},
	},
	// Nitro configuration for API proxy
	nitro: {
		devProxy: {
			"/api": {
				target: "http://127.0.0.1:8000",
				changeOrigin: true,
				prependPath: true,
			},
		},
	},
});
