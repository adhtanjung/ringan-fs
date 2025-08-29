// MongoDB initialization script for Mental Health Chat Application
// This script runs when the MongoDB container starts for the first time

// Switch to the mental health chat database
db = db.getSiblingDB("mental_health_chat");

// Create collections with proper indexes
db.createCollection("conversations");
db.createCollection("users");
db.createCollection("assessments");
db.createCollection("suggestions");
db.createCollection("feedback");

// Create indexes for better performance
db.conversations.createIndex({ user_id: 1 });
db.conversations.createIndex({ created_at: -1 });
db.conversations.createIndex({ session_id: 1 });

db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ username: 1 });

db.assessments.createIndex({ user_id: 1 });
db.assessments.createIndex({ created_at: -1 });
db.assessments.createIndex({ problem_category: 1 });

db.suggestions.createIndex({ user_id: 1 });
db.suggestions.createIndex({ assessment_id: 1 });
db.suggestions.createIndex({ created_at: -1 });

db.feedback.createIndex({ user_id: 1 });
db.feedback.createIndex({ suggestion_id: 1 });
db.feedback.createIndex({ created_at: -1 });

// Create a test user for development
db.users.insertOne({
	username: "test_user",
	email: "test@example.com",
	password_hash: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK8i", // "password123"
	created_at: new Date(),
	updated_at: new Date(),
	is_active: true,
	role: "user",
});

print("✅ MongoDB initialized successfully for Mental Health Chat Application");
print(
	"📊 Collections created: conversations, users, assessments, suggestions, feedback"
);
print("🔍 Indexes created for optimal performance");
print("👤 Test user created: test@example.com / password123");
