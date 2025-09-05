export default defineI18nConfig(() => ({
	legacy: false,
	locale: "id",
	fallbackLocale: "id",
	messages: {
		en: {},
		id: {},
	},
	// Disable strict message checking to prevent SSR errors
	allowComposition: true,
	useScope: "global",
}));
