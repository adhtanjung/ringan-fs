# Mental Health Chatbot - UI/UX Documentation

**Date:** January 2025  
**Version:** 1.0

## Overview

This document provides comprehensive UI/UX guidelines and specifications for the Mental Health Chatbot application. The design philosophy centers on creating a safe, calming, and accessible digital environment that promotes mental well-being while ensuring users feel supported and understood throughout their interaction journey.

## Design Philosophy & Principles

### Core Design Principles

1. **Empathy-First Design**
   - Every interface element should convey understanding and support
   - Use warm, non-judgmental language throughout the application
   - Prioritize emotional safety in all user interactions

2. **Accessibility & Inclusion**
   - Design for users with varying mental health states and technical abilities
   - Ensure compatibility with assistive technologies
   - Provide multiple interaction modalities (text, voice, touch)

3. **Calming Aesthetics**
   - Use soothing color palettes that reduce anxiety
   - Implement clean, uncluttered layouts to minimize cognitive load
   - Incorporate gentle animations and transitions

4. **Privacy & Trust**
   - Make privacy controls visible and easily accessible
   - Use clear, transparent communication about data handling
   - Provide immediate feedback for user actions

5. **Responsive Adaptability**
   - Ensure seamless experience across all devices and screen sizes
   - Optimize for both desktop and mobile interactions
   - Adapt interface based on user context and emotional state

## User Personas & UX Considerations

### Primary Personas

#### 1. The Overwhelmed Student
**UX Needs:**
- Quick access to support without complex onboarding
- Mobile-first design for on-the-go access
- Clear privacy assurances to reduce stigma concerns
- Simple, intuitive navigation under stress

**Design Considerations:**
- Prominent "Start Chat" button on landing
- Minimal form fields during initial interaction
- Clear "Anonymous" indicators
- Quick crisis support access

#### 2. The Stressed Professional
**UX Needs:**
- Efficient, time-conscious interaction flows
- Professional, discrete interface design
- Easy session pause/resume functionality
- Integration with calendar/scheduling systems

**Design Considerations:**
- Streamlined assessment flows
- Progress indicators for time management
- Professional color scheme options
- Quick export/summary features

#### 3. The Curious Individual
**UX Needs:**
- Exploratory, educational interface elements
- Rich content presentation for learning
- Progress tracking and goal setting
- Community or resource discovery features

**Design Considerations:**
- Educational content integration
- Progress visualization dashboards
- Resource library with search functionality
- Mood tracking and analytics

## Interface Design Specifications

### Color Palette

#### Primary Colors
- **Calming Blue**: `#4A90E2` - Primary actions, links
- **Soft Green**: `#7ED321` - Success states, positive feedback
- **Warm Gray**: `#9B9B9B` - Secondary text, borders
- **Pure White**: `#FFFFFF` - Background, cards
- **Deep Navy**: `#2C3E50` - Primary text, headers

#### Emotional State Colors
- **Crisis Red**: `#E74C3C` - Emergency alerts, crisis detection
- **Warning Orange**: `#F39C12` - Caution states, important notices
- **Neutral Beige**: `#F5F5DC` - Neutral emotional states
- **Calm Lavender**: `#E6E6FA` - Relaxation, meditation modes

#### Accessibility Colors
- **High Contrast Mode**: Black `#000000` on White `#FFFFFF`
- **Low Vision Support**: Enhanced contrast ratios (4.5:1 minimum)
- **Color Blind Friendly**: Patterns and icons supplement color coding

### Typography

#### Font Families
- **Primary**: Inter, system-ui, sans-serif
- **Secondary**: Georgia, serif (for longer content)
- **Monospace**: 'Courier New', monospace (for technical content)

#### Font Scales
- **H1**: 2.5rem (40px) - Page titles
- **H2**: 2rem (32px) - Section headers
- **H3**: 1.5rem (24px) - Subsection headers
- **Body**: 1rem (16px) - Main content
- **Small**: 0.875rem (14px) - Secondary information
- **Caption**: 0.75rem (12px) - Metadata, timestamps

#### Line Heights
- **Headers**: 1.2
- **Body Text**: 1.6
- **Chat Messages**: 1.4

### Spacing System

#### Base Unit: 8px
- **XS**: 4px (0.25rem)
- **SM**: 8px (0.5rem)
- **MD**: 16px (1rem)
- **LG**: 24px (1.5rem)
- **XL**: 32px (2rem)
- **2XL**: 48px (3rem)
- **3XL**: 64px (4rem)

### Component Library (shadcn/vue)

#### Buttons

**Primary Button (shadcn/vue)**
```vue
<Button variant="default" size="default" class="bg-[#4A90E2] hover:bg-[#3A7BC8] text-white font-semibold rounded-lg px-6 py-3 focus:ring-2 focus:ring-[#4A90E2] focus:ring-offset-2">
  Primary Action
</Button>
```

**Secondary Button (shadcn/vue)**
```vue
<Button variant="outline" size="default" class="border-2 border-[#4A90E2] text-[#4A90E2] hover:bg-[#4A90E2] hover:text-white rounded-lg px-6 py-3">
  Secondary Action
</Button>
```

**Crisis Button (shadcn/vue)**
```vue
<Button variant="destructive" size="default" class="bg-[#E74C3C] hover:bg-[#C0392B] text-white font-bold rounded-lg px-6 py-3 animate-pulse focus:ring-2 focus:ring-[#E74C3C] focus:ring-offset-2">
  Crisis Support
</Button>
```

#### Input Fields (shadcn/vue)

**Text Input**
```vue
<Input 
  type="text" 
  placeholder="Enter your response..."
  class="border-2 border-[#9B9B9B] focus:border-[#4A90E2] rounded-lg px-4 py-3 text-base transition-colors"
/>
```

**Chat Input with Auto-resize**
```vue
<div class="relative">
  <Textarea 
    placeholder="Type your message..."
    class="min-h-[48px] max-h-[120px] border-2 border-[#9B9B9B] focus:border-[#4A90E2] rounded-3xl px-4 py-3 pr-12 resize-none transition-colors"
    auto-resize
  />
  <Button size="icon" class="absolute right-2 top-1/2 transform -translate-y-1/2 rounded-full">
    <Send class="h-4 w-4" />
  </Button>
</div>
```

**Interactive Option Selector**
```vue
<RadioGroup v-model="selectedOption" class="space-y-3">
  <div class="flex items-center space-x-2 p-3 rounded-lg border hover:bg-gray-50 cursor-pointer">
    <RadioGroupItem value="option1" id="option1" />
    <Label for="option1" class="flex-1 cursor-pointer">Strongly Disagree</Label>
  </div>
  <div class="flex items-center space-x-2 p-3 rounded-lg border hover:bg-gray-50 cursor-pointer">
    <RadioGroupItem value="option2" id="option2" />
    <Label for="option2" class="flex-1 cursor-pointer">Disagree</Label>
  </div>
</RadioGroup>
```

#### Cards (shadcn/vue)

**Message Card**
```vue
<Card class="bg-white rounded-2xl p-4 shadow-sm border-0 my-2">
  <CardContent class="p-0">
    <div class="flex items-start space-x-3">
      <Avatar class="w-8 h-8">
        <AvatarImage src="/ai-avatar.png" />
        <AvatarFallback>AI</AvatarFallback>
      </Avatar>
      <div class="flex-1">
        <p class="text-sm text-gray-600 mb-1">AI Assistant</p>
        <p class="text-base leading-relaxed">{{ message.content }}</p>
      </div>
    </div>
  </CardContent>
</Card>
```

**Assessment Card with Progress**
```vue
<Card class="bg-gradient-to-br from-blue-50 to-indigo-50 border border-[#9B9B9B] rounded-xl p-6">
  <CardHeader class="p-0 mb-4">
    <Progress :value="progressValue" class="h-2" />
    <p class="text-sm text-gray-600 mt-2">Question {{ currentQuestion }} of {{ totalQuestions }}</p>
  </CardHeader>
  <CardContent class="p-0">
    <!-- Assessment content -->
  </CardContent>
</Card>
```

**Interactive Chat Bubble**
```vue
<div class="flex justify-end mb-4">
  <Card class="bg-[#4A90E2] text-white rounded-2xl rounded-br-md max-w-xs p-3">
    <CardContent class="p-0">
      <p class="text-sm">{{ userMessage }}</p>
      <p class="text-xs opacity-75 mt-1">{{ timestamp }}</p>
    </CardContent>
  </Card>
</div>
```

#### Navigation

**Top Navigation**
- Height: 64px
- Background: White with subtle shadow
- Logo/title on left
- User controls on right
- Language switcher
- Settings/menu icon

**Mobile Navigation**
- Bottom tab bar for primary actions
- Height: 56px
- Icons with labels
- Active state highlighting

## Interactive AI Chat Conversation System

### Core Chat Architecture

#### Real-time Conversation Flow
```vue
<template>
  <div class="flex flex-col h-screen bg-gray-50">
    <!-- Chat Header -->
    <div class="bg-white border-b px-4 py-3 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <Avatar class="w-10 h-10">
          <AvatarImage src="/ai-therapist.png" />
          <AvatarFallback class="bg-[#4A90E2] text-white">AI</AvatarFallback>
        </Avatar>
        <div>
          <h3 class="font-semibold text-gray-900">Mental Health Assistant</h3>
          <p class="text-sm text-green-600 flex items-center">
            <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            Online & Ready to Help
          </p>
        </div>
      </div>
      <Button variant="ghost" size="icon">
        <MoreVertical class="h-5 w-5" />
      </Button>
    </div>

    <!-- Messages Container -->
    <ScrollArea class="flex-1 px-4 py-6">
      <div class="space-y-4 max-w-4xl mx-auto">
        <!-- AI Message with Quick Actions -->
        <div class="flex items-start space-x-3">
          <Avatar class="w-8 h-8">
            <AvatarImage src="/ai-avatar.png" />
            <AvatarFallback class="bg-[#4A90E2] text-white text-xs">AI</AvatarFallback>
          </Avatar>
          <div class="flex-1 max-w-md">
            <Card class="bg-white border-0 shadow-sm">
              <CardContent class="p-4">
                <p class="text-gray-800 leading-relaxed">{{ aiMessage }}</p>
                <div class="flex flex-wrap gap-2 mt-3" v-if="quickReplies.length > 0">
                  <Button 
                    v-for="reply in quickReplies" 
                    :key="reply.id"
                    variant="outline" 
                    size="sm"
                    class="text-xs rounded-full"
                    @click="selectQuickReply(reply)"
                  >
                    {{ reply.text }}
                  </Button>
                </div>
              </CardContent>
            </Card>
            <p class="text-xs text-gray-500 mt-1 ml-4">{{ timestamp }}</p>
          </div>
        </div>

        <!-- User Message -->
        <div class="flex justify-end">
          <div class="max-w-md">
            <Card class="bg-[#4A90E2] text-white border-0">
              <CardContent class="p-4">
                <p class="leading-relaxed">{{ userMessage }}</p>
              </CardContent>
            </Card>
            <p class="text-xs text-gray-500 mt-1 mr-4 text-right">{{ timestamp }}</p>
          </div>
        </div>
      </div>
    </ScrollArea>

    <!-- Input Area -->
    <div class="bg-white border-t px-4 py-4">
      <div class="max-w-4xl mx-auto">
        <div class="relative flex items-end space-x-3">
          <div class="flex-1">
            <Textarea 
              v-model="currentMessage"
              placeholder="Share what's on your mind..."
              class="min-h-[48px] max-h-[120px] border-2 border-gray-200 focus:border-[#4A90E2] rounded-2xl px-4 py-3 pr-12 resize-none transition-colors"
              @keydown.enter.prevent="sendMessage"
            />
            <Button 
              size="icon" 
              class="absolute right-2 bottom-2 rounded-full"
              @click="sendMessage"
              :disabled="!currentMessage.trim()"
            >
              <Send class="h-4 w-4" />
            </Button>
          </div>
          <Button variant="outline" size="icon" class="rounded-full">
            <Mic class="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
```

### Conversation Intelligence Features

#### Emotion Detection & Response
```vue
<div class="flex items-center space-x-2 mt-2" v-if="detectedEmotion">
  <Badge variant="secondary" class="text-xs">
    <Heart class="w-3 h-3 mr-1" />
    {{ detectedEmotion.label }}
  </Badge>
  <Button variant="ghost" size="sm" class="text-xs h-6 px-2">
    Suggest coping strategies
  </Button>
</div>
```

#### Crisis Detection Alert
```vue
<Alert class="border-red-200 bg-red-50 mb-4" v-if="crisisDetected">
  <AlertTriangle class="h-4 w-4 text-red-600" />
  <AlertTitle class="text-red-800">Immediate Support Available</AlertTitle>
  <AlertDescription class="text-red-700">
    I notice you might be going through a difficult time. Would you like to connect with a crisis counselor?
    <div class="flex space-x-2 mt-3">
      <Button size="sm" class="bg-red-600 hover:bg-red-700">
        <Phone class="w-4 h-4 mr-2" />
        Call Crisis Line
      </Button>
      <Button variant="outline" size="sm">
        <MessageCircle class="w-4 h-4 mr-2" />
        Chat with Counselor
      </Button>
    </div>
  </AlertDescription>
</Alert>
```

## Intuitive Self-Assessment UI System

### Progressive Assessment Flow

#### Assessment Introduction Card
```vue
<Card class="max-w-2xl mx-auto bg-gradient-to-br from-blue-50 to-indigo-100 border-0 shadow-lg">
  <CardHeader class="text-center pb-6">
    <div class="w-16 h-16 bg-[#4A90E2] rounded-full flex items-center justify-center mx-auto mb-4">
      <ClipboardList class="w-8 h-8 text-white" />
    </div>
    <CardTitle class="text-2xl text-gray-900">Mental Health Check-In</CardTitle>
    <CardDescription class="text-gray-600 text-base">
      This brief assessment helps us understand how you're feeling and provide personalized support.
    </CardDescription>
  </CardHeader>
  <CardContent class="space-y-6">
    <div class="flex items-center justify-between text-sm text-gray-600">
      <span class="flex items-center">
        <Clock class="w-4 h-4 mr-2" />
        5-7 minutes
      </span>
      <span class="flex items-center">
        <Shield class="w-4 h-4 mr-2" />
        Completely confidential
      </span>
    </div>
    <Progress :value="0" class="h-2" />
    <Button class="w-full" size="lg">
      Begin Assessment
      <ArrowRight class="w-4 h-4 ml-2" />
    </Button>
  </CardContent>
</Card>
```

#### Interactive Question Types

**Likert Scale Question**
```vue
<Card class="max-w-2xl mx-auto">
  <CardHeader>
    <div class="flex items-center justify-between mb-4">
      <Badge variant="outline">Question {{ currentQuestion }} of {{ totalQuestions }}</Badge>
      <Progress :value="(currentQuestion / totalQuestions) * 100" class="w-32 h-2" />
    </div>
    <CardTitle class="text-xl">{{ question.title }}</CardTitle>
    <CardDescription>{{ question.description }}</CardDescription>
  </CardHeader>
  <CardContent class="space-y-6">
    <RadioGroup v-model="selectedValue" class="space-y-3">
      <div 
        v-for="(option, index) in likertOptions" 
        :key="index"
        class="flex items-center space-x-3 p-4 rounded-lg border-2 hover:border-[#4A90E2] hover:bg-blue-50 cursor-pointer transition-all"
        :class="selectedValue === option.value ? 'border-[#4A90E2] bg-blue-50' : 'border-gray-200'"
      >
        <RadioGroupItem :value="option.value" :id="`option-${index}`" />
        <Label :for="`option-${index}`" class="flex-1 cursor-pointer font-medium">
          {{ option.label }}
        </Label>
        <div class="text-2xl">{{ option.emoji }}</div>
      </div>
    </RadioGroup>
    
    <div class="flex justify-between pt-4">
      <Button variant="outline" @click="previousQuestion" :disabled="currentQuestion === 1">
        <ArrowLeft class="w-4 h-4 mr-2" />
        Previous
      </Button>
      <Button @click="nextQuestion" :disabled="!selectedValue">
        Next
        <ArrowRight class="w-4 h-4 ml-2" />
      </Button>
    </div>
  </CardContent>
</Card>
```

**Visual Mood Selector**
```vue
<div class="grid grid-cols-5 gap-4">
  <div 
    v-for="mood in moodOptions" 
    :key="mood.id"
    class="flex flex-col items-center p-4 rounded-xl border-2 cursor-pointer transition-all hover:scale-105"
    :class="selectedMood === mood.id ? 'border-[#4A90E2] bg-blue-50' : 'border-gray-200 hover:border-gray-300'"
    @click="selectMood(mood.id)"
  >
    <div class="text-4xl mb-2">{{ mood.emoji }}</div>
    <span class="text-sm font-medium text-center">{{ mood.label }}</span>
  </div>
</div>
```

**Slider Assessment**
```vue
<div class="space-y-6">
  <div class="text-center">
    <h3 class="text-lg font-semibold mb-2">{{ question.title }}</h3>
    <p class="text-gray-600">{{ question.subtitle }}</p>
  </div>
  
  <div class="px-4">
    <Slider 
      v-model="sliderValue" 
      :max="10" 
      :min="0" 
      :step="1"
      class="w-full"
    />
    <div class="flex justify-between text-sm text-gray-500 mt-2">
      <span>{{ question.minLabel }}</span>
      <span class="font-semibold text-[#4A90E2]">{{ sliderValue }}/10</span>
      <span>{{ question.maxLabel }}</span>
    </div>
  </div>
  
  <div class="text-center">
    <div class="inline-flex items-center space-x-2 bg-blue-50 rounded-full px-4 py-2">
      <div class="text-2xl">{{ getCurrentMoodEmoji(sliderValue) }}</div>
      <span class="font-medium">{{ getCurrentMoodLabel(sliderValue) }}</span>
    </div>
  </div>
</div>
```

## Predefined Interactive Options System

### Quick Response Templates

#### Conversation Starters
```vue
<div class="space-y-4">
  <h3 class="text-lg font-semibold text-gray-800">How can I help you today?</h3>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
    <Button 
      v-for="starter in conversationStarters" 
      :key="starter.id"
      variant="outline" 
      class="justify-start h-auto p-4 text-left"
      @click="selectStarter(starter)"
    >
      <div class="flex items-start space-x-3">
        <div class="text-2xl">{{ starter.icon }}</div>
        <div>
          <div class="font-medium">{{ starter.title }}</div>
          <div class="text-sm text-gray-500">{{ starter.description }}</div>
        </div>
      </div>
    </Button>
  </div>
</div>
```

#### Feeling Check-in Options
```vue
<div class="space-y-4">
  <h3 class="text-lg font-semibold">How are you feeling right now?</h3>
  <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
    <Card 
      v-for="feeling in feelingOptions" 
      :key="feeling.id"
      class="cursor-pointer transition-all hover:scale-105 hover:shadow-md"
      :class="selectedFeeling === feeling.id ? 'ring-2 ring-[#4A90E2] bg-blue-50' : ''"
      @click="selectFeeling(feeling)"
    >
      <CardContent class="p-4 text-center">
        <div class="text-3xl mb-2">{{ feeling.emoji }}</div>
        <div class="font-medium text-sm">{{ feeling.label }}</div>
      </CardContent>
    </Card>
  </div>
</div>
```

#### Coping Strategy Suggestions
```vue
<div class="space-y-4">
  <h3 class="text-lg font-semibold">Try these coping strategies:</h3>
  <div class="space-y-3">
    <Card 
      v-for="strategy in copingStrategies" 
      :key="strategy.id"
      class="cursor-pointer hover:shadow-md transition-all"
      @click="startStrategy(strategy)"
    >
      <CardContent class="p-4">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center">
            <component :is="strategy.icon" class="w-6 h-6 text-[#4A90E2]" />
          </div>
          <div class="flex-1">
            <h4 class="font-semibold">{{ strategy.title }}</h4>
            <p class="text-sm text-gray-600">{{ strategy.description }}</p>
            <div class="flex items-center mt-2">
              <Clock class="w-4 h-4 mr-1 text-gray-400" />
              <span class="text-xs text-gray-500">{{ strategy.duration }}</span>
            </div>
          </div>
          <ChevronRight class="w-5 h-5 text-gray-400" />
        </div>
      </CardContent>
    </Card>
  </div>
</div>
```

### Interactive Assessment Results

#### Results Dashboard
```vue
<Card class="max-w-4xl mx-auto">
  <CardHeader class="text-center">
    <div class="w-20 h-20 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
      <CheckCircle class="w-10 h-10 text-white" />
    </div>
    <CardTitle class="text-2xl">Assessment Complete</CardTitle>
    <CardDescription>Here's your personalized mental health insights</CardDescription>
  </CardHeader>
  
  <CardContent class="space-y-8">
    <!-- Overall Score -->
    <div class="text-center">
      <div class="inline-flex items-center space-x-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6">
        <div class="text-4xl font-bold text-[#4A90E2]">{{ overallScore }}/100</div>
        <div>
          <div class="font-semibold text-lg">Overall Wellbeing</div>
          <div class="text-sm text-gray-600">{{ getScoreDescription(overallScore) }}</div>
        </div>
      </div>
    </div>
    
    <!-- Category Breakdown -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div v-for="category in assessmentCategories" :key="category.id" class="text-center">
        <div class="w-16 h-16 mx-auto mb-3 relative">
          <svg class="w-16 h-16 transform -rotate-90">
            <circle cx="32" cy="32" r="28" stroke="#e5e7eb" stroke-width="4" fill="none" />
            <circle 
              cx="32" cy="32" r="28" 
              :stroke="category.color" 
              stroke-width="4" 
              fill="none"
              :stroke-dasharray="`${(category.score / 100) * 175.93} 175.93`"
              class="transition-all duration-1000"
            />
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-sm font-bold">{{ category.score }}</span>
          </div>
        </div>
        <h4 class="font-semibold">{{ category.name }}</h4>
        <p class="text-sm text-gray-600">{{ category.description }}</p>
      </div>
    </div>
    
    <!-- Recommendations -->
    <div class="space-y-4">
      <h3 class="text-xl font-semibold">Personalized Recommendations</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card v-for="recommendation in recommendations" :key="recommendation.id" class="cursor-pointer hover:shadow-md transition-all">
          <CardContent class="p-4">
            <div class="flex items-start space-x-3">
              <div class="w-10 h-10 bg-gradient-to-br from-purple-100 to-pink-100 rounded-lg flex items-center justify-center">
                <component :is="recommendation.icon" class="w-5 h-5 text-purple-600" />
              </div>
              <div class="flex-1">
                <h4 class="font-semibold mb-1">{{ recommendation.title }}</h4>
                <p class="text-sm text-gray-600 mb-2">{{ recommendation.description }}</p>
                <Button size="sm" variant="outline">
                  {{ recommendation.action }}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  </CardContent>
</Card>
```

## Seamless User Interaction & Navigation

### Intelligent Navigation System

#### Contextual Navigation Bar
```vue
<nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between h-16">
      <div class="flex items-center">
        <div class="flex-shrink-0 flex items-center">
          <img class="h-8 w-auto" src="/logo.svg" alt="Mental Health Assistant" />
          <span class="ml-2 text-xl font-semibold text-gray-900">Ringan</span>
        </div>
        
        <!-- Breadcrumb Navigation -->
        <nav class="hidden md:flex ml-8" aria-label="Breadcrumb">
          <ol class="flex items-center space-x-4">
            <li v-for="(item, index) in breadcrumbs" :key="index">
              <div class="flex items-center">
                <ChevronRight v-if="index > 0" class="flex-shrink-0 h-4 w-4 text-gray-400" />
                <a 
                  :href="item.href" 
                  class="ml-4 text-sm font-medium text-gray-500 hover:text-gray-700"
                  :class="{ 'text-gray-900': index === breadcrumbs.length - 1 }"
                >
                  {{ item.name }}
                </a>
              </div>
            </li>
          </ol>
        </nav>
      </div>
      
      <div class="flex items-center space-x-4">
        <!-- Progress Indicator -->
        <div v-if="showProgress" class="hidden sm:flex items-center space-x-2">
          <div class="text-sm text-gray-600">Progress:</div>
          <Progress :value="progressPercentage" class="w-24 h-2" />
          <span class="text-sm font-medium text-gray-900">{{ progressPercentage }}%</span>
        </div>
        
        <!-- Quick Actions -->
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <MoreHorizontal class="h-5 w-5" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <Save class="mr-2 h-4 w-4" />
              Save Progress
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Download class="mr-2 h-4 w-4" />
              Export Chat
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <Settings class="mr-2 h-4 w-4" />
              Settings
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        
        <!-- Emergency Button -->
        <Button variant="destructive" size="sm" class="animate-pulse">
          <Phone class="w-4 h-4 mr-2" />
          Crisis Help
        </Button>
      </div>
    </div>
  </div>
</nav>
```

#### Smart Sidebar Navigation
```vue
<aside class="w-64 bg-white border-r border-gray-200 fixed inset-y-0 left-0 z-40 transform transition-transform duration-300 ease-in-out lg:translate-x-0">
  <div class="flex flex-col h-full">
    <!-- User Status -->
    <div class="p-4 border-b border-gray-200">
      <div class="flex items-center space-x-3">
        <Avatar class="w-10 h-10">
          <AvatarImage :src="user.avatar" />
          <AvatarFallback class="bg-[#4A90E2] text-white">{{ user.initials }}</AvatarFallback>
        </Avatar>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 truncate">{{ user.name || 'Anonymous User' }}</p>
          <p class="text-xs text-gray-500">{{ currentSessionTime }}</p>
        </div>
      </div>
    </div>
    
    <!-- Navigation Menu -->
    <nav class="flex-1 px-4 py-4 space-y-2">
      <div v-for="section in navigationSections" :key="section.id" class="space-y-1">
        <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider">{{ section.title }}</h3>
        <div class="space-y-1">
          <a 
            v-for="item in section.items" 
            :key="item.id"
            :href="item.href"
            class="group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
            :class="item.current ? 'bg-[#4A90E2] text-white' : 'text-gray-700 hover:bg-gray-100'"
          >
            <component :is="item.icon" class="mr-3 h-5 w-5" :class="item.current ? 'text-white' : 'text-gray-400'" />
            {{ item.name }}
            <Badge v-if="item.badge" variant="secondary" class="ml-auto">{{ item.badge }}</Badge>
          </a>
        </div>
      </div>
    </nav>
    
    <!-- Quick Stats -->
    <div class="p-4 border-t border-gray-200">
      <div class="space-y-3">
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-600">Sessions completed</span>
          <span class="font-semibold text-gray-900">{{ userStats.sessionsCompleted }}</span>
        </div>
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-600">Current streak</span>
          <span class="font-semibold text-green-600">{{ userStats.currentStreak }} days</span>
        </div>
      </div>
    </div>
  </div>
</aside>
```

### Adaptive Interface Components

#### Context-Aware Action Bar
```vue
<div class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 z-30">
  <div class="max-w-4xl mx-auto">
    <div class="flex items-center justify-between">
      <!-- Context Actions -->
      <div class="flex items-center space-x-3">
        <Button 
          v-if="canGoBack" 
          variant="outline" 
          size="sm"
          @click="goBack"
        >
          <ArrowLeft class="w-4 h-4 mr-2" />
          Back
        </Button>
        
        <Button 
          v-if="canSaveProgress" 
          variant="ghost" 
          size="sm"
          @click="saveProgress"
        >
          <Save class="w-4 h-4 mr-2" />
          Save
        </Button>
      </div>
      
      <!-- Primary Action -->
      <div class="flex items-center space-x-3">
        <Button 
          v-if="showSkipOption" 
          variant="ghost" 
          size="sm"
          @click="skipStep"
        >
          Skip for now
        </Button>
        
        <Button 
          :disabled="!canProceed"
          @click="proceedToNext"
          class="min-w-[120px]"
        >
          {{ primaryActionText }}
          <ArrowRight class="w-4 h-4 ml-2" />
        </Button>
      </div>
    </div>
  </div>
</div>
```

#### Smart Input Suggestions
```vue
<div class="relative">
  <Textarea 
    v-model="userInput"
    placeholder="Share what's on your mind..."
    class="min-h-[100px] pr-12"
    @input="handleInputChange"
    @focus="showSuggestions = true"
  />
  
  <!-- AI Suggestions Overlay -->
  <div 
    v-if="showSuggestions && suggestions.length > 0" 
    class="absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-lg shadow-lg mt-1 z-10"
  >
    <div class="p-3 border-b border-gray-100">
      <h4 class="text-sm font-medium text-gray-700">Suggested responses:</h4>
    </div>
    <div class="max-h-48 overflow-y-auto">
      <button 
        v-for="suggestion in suggestions" 
        :key="suggestion.id"
        class="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 transition-colors"
        @click="selectSuggestion(suggestion)"
      >
        <div class="flex items-start space-x-2">
          <div class="text-lg">{{ suggestion.emoji }}</div>
          <div class="flex-1">
            <div class="font-medium text-gray-900">{{ suggestion.title }}</div>
            <div class="text-gray-600">{{ suggestion.preview }}</div>
          </div>
        </div>
      </button>
    </div>
  </div>
</div>
```

## Enhanced UX Principles Implementation

### Micro-Interactions & Feedback

#### Loading States with Personality
```vue
<div class="flex flex-col items-center justify-center py-12">
  <div class="relative">
    <!-- Animated AI Avatar -->
    <div class="w-16 h-16 bg-gradient-to-br from-[#4A90E2] to-[#7ED321] rounded-full flex items-center justify-center animate-pulse">
      <Brain class="w-8 h-8 text-white" />
    </div>
    
    <!-- Thinking Animation -->
    <div class="absolute -top-2 -right-2">
      <div class="flex space-x-1">
        <div class="w-2 h-2 bg-[#4A90E2] rounded-full animate-bounce" style="animation-delay: 0ms"></div>
        <div class="w-2 h-2 bg-[#4A90E2] rounded-full animate-bounce" style="animation-delay: 150ms"></div>
        <div class="w-2 h-2 bg-[#4A90E2] rounded-full animate-bounce" style="animation-delay: 300ms"></div>
      </div>
    </div>
  </div>
  
  <div class="mt-4 text-center">
    <p class="text-lg font-medium text-gray-900">{{ loadingMessage }}</p>
    <p class="text-sm text-gray-600 mt-1">{{ loadingSubtext }}</p>
  </div>
  
  <!-- Progress Bar -->
  <div class="w-64 mt-6">
    <Progress :value="loadingProgress" class="h-2" />
  </div>
</div>
```

#### Success Celebrations
```vue
<div class="fixed inset-0 flex items-center justify-center z-50 pointer-events-none">
  <div class="bg-white rounded-2xl shadow-2xl p-8 text-center transform transition-all duration-500" :class="showCelebration ? 'scale-100 opacity-100' : 'scale-95 opacity-0'">
    <!-- Confetti Animation -->
    <div class="absolute inset-0 overflow-hidden rounded-2xl">
      <div v-for="i in 20" :key="i" class="absolute animate-ping" :style="getConfettiStyle(i)">
        <div class="w-2 h-2 bg-gradient-to-r from-yellow-400 to-pink-500 rounded-full"></div>
      </div>
    </div>
    
    <div class="relative z-10">
      <div class="w-20 h-20 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
        <CheckCircle class="w-10 h-10 text-white" />
      </div>
      <h3 class="text-2xl font-bold text-gray-900 mb-2">{{ celebrationTitle }}</h3>
      <p class="text-gray-600">{{ celebrationMessage }}</p>
    </div>
  </div>
</div>
```

### Accessibility-First Design

#### Keyboard Navigation Enhancement
```vue
<div 
  class="focus-within:ring-2 focus-within:ring-[#4A90E2] focus-within:ring-offset-2 rounded-lg"
  @keydown="handleKeyNavigation"
  tabindex="0"
>
  <!-- Skip Links -->
  <div class="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 z-50">
    <a href="#main-content" class="bg-[#4A90E2] text-white px-4 py-2 rounded-md text-sm font-medium">
      Skip to main content
    </a>
  </div>
  
  <!-- ARIA Live Region for Dynamic Updates -->
  <div aria-live="polite" aria-atomic="true" class="sr-only">
    {{ screenReaderAnnouncement }}
  </div>
  
  <!-- Focus Trap for Modals -->
  <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="absolute inset-0 bg-black bg-opacity-50" @click="closeModal"></div>
    <div 
      class="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4"
      role="dialog"
      aria-labelledby="modal-title"
      aria-describedby="modal-description"
    >
      <!-- Modal content with proper focus management -->
    </div>
  </div>
</div>
```

#### Screen Reader Optimizations
```vue
<template>
  <!-- Semantic HTML Structure -->
  <main id="main-content" role="main" aria-labelledby="page-title">
    <h1 id="page-title" class="sr-only">Mental Health Chat Interface</h1>
    
    <!-- Chat Messages with Proper ARIA -->
    <section aria-label="Conversation history" role="log" aria-live="polite">
      <div 
        v-for="message in messages" 
        :key="message.id"
        :aria-label="`${message.sender} said: ${message.content} at ${message.timestamp}`"
        class="message-item"
      >
        <div class="sr-only">{{ message.sender }} message:</div>
        <div>{{ message.content }}</div>
      </div>
    </section>
    
    <!-- Input Form with Proper Labels -->
    <form @submit.prevent="sendMessage" aria-label="Send message form">
      <label for="message-input" class="sr-only">Type your message</label>
      <textarea 
        id="message-input"
        v-model="currentMessage"
        aria-describedby="message-help"
        aria-required="true"
        placeholder="Share what's on your mind..."
      ></textarea>
      <div id="message-help" class="sr-only">
        Type your message and press Enter to send, or use the send button
      </div>
      <button type="submit" aria-label="Send message">
        <Send class="w-4 h-4" aria-hidden="true" />
        <span class="sr-only">Send</span>
      </button>
    </form>
  </main>
</template>
```

### Performance Optimization

#### Lazy Loading Components
```vue
<template>
  <div>
    <!-- Critical Above-the-fold Content -->
    <ChatHeader />
    <MessageList :messages="visibleMessages" />
    
    <!-- Lazy Load Non-critical Components -->
    <Suspense>
      <template #default>
        <LazyAssessmentPanel v-if="showAssessment" />
      </template>
      <template #fallback>
        <div class="flex items-center justify-center py-8">
          <Loader2 class="w-6 h-6 animate-spin" />
          <span class="ml-2 text-sm text-gray-600">Loading assessment...</span>
        </div>
      </template>
    </Suspense>
    
    <!-- Virtual Scrolling for Large Message Lists -->
    <VirtualList 
      :items="allMessages"
      :item-height="80"
      :visible-count="10"
      v-slot="{ item }"
    >
      <MessageBubble :message="item" />
    </VirtualList>
  </div>
</template>

<script setup>
// Lazy load heavy components
const LazyAssessmentPanel = defineAsyncComponent(() => import('./AssessmentPanel.vue'))
const LazyResourceLibrary = defineAsyncComponent(() => import('./ResourceLibrary.vue'))
</script>
```

#### Optimistic UI Updates
```vue
<script setup>
const sendMessage = async (content) => {
  // Optimistically add message to UI
  const optimisticMessage = {
    id: `temp-${Date.now()}`,
    content,
    sender: 'user',
    timestamp: new Date(),
    status: 'sending'
  }
  
  messages.value.push(optimisticMessage)
  
  try {
    // Send to backend
    const response = await api.sendMessage(content)
    
    // Update with real data
    const messageIndex = messages.value.findIndex(m => m.id === optimisticMessage.id)
    if (messageIndex !== -1) {
      messages.value[messageIndex] = {
        ...response.data,
        status: 'sent'
      }
    }
  } catch (error) {
    // Handle error - mark message as failed
    const messageIndex = messages.value.findIndex(m => m.id === optimisticMessage.id)
    if (messageIndex !== -1) {
      messages.value[messageIndex].status = 'failed'
    }
  }
}
</script>
```

## User Experience Flows

### 1. Onboarding Flow

#### Welcome Screen
- **Hero Section**: Welcoming illustration with calming colors
- **Value Proposition**: Clear, empathetic messaging about support
- **Privacy Assurance**: Prominent privacy and anonymity statements
- **CTA**: "Start Your Journey" button

#### Disclaimer & Consent
- **Medical Disclaimer**: Clear, non-intimidating language
- **Data Usage**: Transparent privacy policy summary
- **Consent Checkboxes**: Required agreements
- **Emergency Resources**: Always-visible crisis support links

#### Initial Preference Setting
- **Language Selection**: Indonesian/English toggle
- **Communication Preference**: Text, voice, or both
- **Concern Category** (Optional): Stress, Anxiety, Trauma, Not Sure
- **Skip Option**: Allow immediate chat access

### 2. Chat Interface Flow

#### Chat Initialization
- **Greeting Message**: Warm, personalized welcome
- **Typing Indicators**: Show AI is "thinking"
- **Quick Suggestions**: Conversation starters
- **Voice Toggle**: Easy access to speech features

#### Conversation Flow
- **Message Bubbles**: Distinct styling for user vs AI
- **Timestamp Display**: Subtle, non-intrusive
- **Streaming Responses**: Real-time text appearance
- **Emotion Indicators**: Visual cues for detected emotions
- **Crisis Detection**: Immediate intervention interface

#### Assessment Integration
- **Smooth Transition**: From chat to structured assessment
- **Progress Visualization**: Clear completion indicators
- **Question Types**: 
  - Scale responses with visual sliders
  - Text inputs with character guidance
  - Multiple choice with clear selection states
- **Navigation**: Back/forward with progress preservation

### 3. Crisis Support Flow

#### Crisis Detection
- **Immediate Alert**: Non-alarming but urgent notification
- **Resource Display**: Emergency contacts prominently shown
- **WhatsApp Integration**: One-click support access
- **Dismissal Option**: User control over alert visibility

#### Emergency Resources
- **Contact Cards**: Professional, trustworthy design
- **Quick Actions**: Call, message, or visit website
- **Location-Based**: Relevant local resources
- **24/7 Indicators**: Clear availability information

### 4. Assessment Flow

#### Assessment Initiation
- **Context Setting**: Explanation of assessment purpose
- **Time Estimation**: Expected completion duration
- **Progress Tracking**: Visual progress bar
- **Pause/Resume**: Flexible completion options

#### Question Presentation
- **Single Question Focus**: One question per screen
- **Clear Instructions**: Response format guidance
- **Visual Aids**: Icons, illustrations for clarity
- **Validation**: Real-time input validation

#### Results & Recommendations
- **Summary View**: Assessment completion acknowledgment
- **Personalized Suggestions**: Tailored recommendations
- **Resource Links**: External resources with descriptions

### 5. Intelligent Conversation Flow Management

#### Dynamic Question Routing
```vue
<template>
  <div class="conversation-flow-container">
    <!-- Flow Progress Indicator -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium text-gray-700">Assessment Progress</span>
        <span class="text-sm text-gray-500">{{ currentStep }} of {{ totalSteps }}</span>
      </div>
      <Progress :value="(currentStep / totalSteps) * 100" class="h-2" />
    </div>
    
    <!-- Dynamic Question Component -->
    <component 
      :is="currentQuestionComponent" 
      :question="currentQuestion"
      :options="currentOptions"
      @answer="handleAnswer"
      @skip="handleSkip"
      @back="handleBack"
    />
    
    <!-- Navigation Hints -->
    <div class="mt-6 flex items-center justify-between text-sm text-gray-500">
      <div class="flex items-center space-x-2">
        <Lightbulb class="w-4 h-4" />
        <span>{{ navigationHint }}</span>
      </div>
      <div class="flex items-center space-x-2">
        <Clock class="w-4 h-4" />
        <span>~{{ estimatedTimeRemaining }} min remaining</span>
      </div>
    </div>
  </div>
</template>

<script setup>
const questionComponents = {
  'likert-scale': LikertScaleQuestion,
  'mood-selector': MoodSelectorQuestion,
  'slider': SliderQuestion,
  'multiple-choice': MultipleChoiceQuestion,
  'binary': BinaryChoiceQuestion,
  'priority-ranking': PriorityRankingQuestion
}

const currentQuestionComponent = computed(() => {
  return questionComponents[currentQuestion.value?.type] || MultipleChoiceQuestion
})
</script>
```

#### Adaptive Response System
```vue
<template>
  <div class="adaptive-response-system">
    <!-- AI Response with Emotional Context -->
    <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 mb-4">
      <div class="flex items-start space-x-3">
        <div class="flex-shrink-0">
          <div class="w-8 h-8 bg-gradient-to-br from-[#4A90E2] to-[#7ED321] rounded-full flex items-center justify-center">
            <Bot class="w-4 h-4 text-white" />
          </div>
        </div>
        <div class="flex-1">
          <div class="flex items-center space-x-2 mb-2">
            <span class="text-sm font-medium text-gray-900">AI Assistant</span>
            <Badge variant="secondary" class="text-xs">{{ responseContext.emotionalTone }}</Badge>
          </div>
          <div class="prose prose-sm text-gray-700">
            <p>{{ adaptiveResponse.content }}</p>
          </div>
          
          <!-- Contextual Actions -->
          <div class="mt-3 flex flex-wrap gap-2">
            <Button 
              v-for="action in adaptiveResponse.suggestedActions" 
              :key="action.id"
              variant="outline" 
              size="sm"
              @click="handleSuggestedAction(action)"
            >
              <component :is="action.icon" class="w-4 h-4 mr-2" />
              {{ action.label }}
            </Button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Follow-up Questions -->
    <div v-if="followUpQuestions.length > 0" class="space-y-2">
      <h4 class="text-sm font-medium text-gray-700 mb-3">Would you like to explore:</h4>
      <div class="grid gap-2">
        <button 
          v-for="question in followUpQuestions" 
          :key="question.id"
          class="text-left p-3 rounded-lg border border-gray-200 hover:border-[#4A90E2] hover:bg-blue-50 transition-colors"
          @click="selectFollowUp(question)"
        >
          <div class="flex items-center space-x-3">
            <div class="text-lg">{{ question.emoji }}</div>
            <div class="flex-1">
              <div class="font-medium text-gray-900">{{ question.title }}</div>
              <div class="text-sm text-gray-600">{{ question.description }}</div>
            </div>
            <ArrowRight class="w-4 h-4 text-gray-400" />
          </div>
        </button>
      </div>
    </div>
  </div>
</template>
```

### 6. Crisis Detection & Support Integration

#### Real-time Crisis Detection UI
```vue
<template>
  <div v-if="crisisDetected" class="fixed inset-0 bg-red-900 bg-opacity-90 flex items-center justify-center z-50">
    <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 p-6">
      <!-- Crisis Alert Header -->
      <div class="text-center mb-6">
        <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <AlertTriangle class="w-8 h-8 text-red-600" />
        </div>
        <h2 class="text-xl font-bold text-gray-900 mb-2">We're Here to Help</h2>
        <p class="text-gray-600">It sounds like you might be going through a difficult time. You're not alone.</p>
      </div>
      
      <!-- Immediate Actions -->
      <div class="space-y-3 mb-6">
        <Button 
          variant="destructive" 
          size="lg" 
          class="w-full justify-start"
          @click="callCrisisHotline"
        >
          <Phone class="w-5 h-5 mr-3" />
          Call Crisis Hotline
          <span class="ml-auto text-sm opacity-75">24/7 Available</span>
        </Button>
        
        <Button 
          variant="outline" 
          size="lg" 
          class="w-full justify-start"
          @click="startCrisisChat"
        >
          <MessageCircle class="w-5 h-5 mr-3" />
          Chat with Crisis Counselor
          <span class="ml-auto text-sm opacity-75">Live Support</span>
        </Button>
        
        <Button 
          variant="ghost" 
          size="lg" 
          class="w-full justify-start"
          @click="viewCopingStrategies"
        >
          <Heart class="w-5 h-5 mr-3" />
          Immediate Coping Strategies
        </Button>
      </div>
      
      <!-- Safety Planning -->
      <div class="border-t border-gray-200 pt-4">
        <h3 class="font-medium text-gray-900 mb-3">Quick Safety Check:</h3>
        <div class="space-y-2">
          <label class="flex items-center space-x-3">
            <Checkbox v-model="safetyChecks.safeLocation" />
            <span class="text-sm text-gray-700">I am in a safe location</span>
          </label>
          <label class="flex items-center space-x-3">
            <Checkbox v-model="safetyChecks.supportPerson" />
            <span class="text-sm text-gray-700">I have someone I can reach out to</span>
          </label>
          <label class="flex items-center space-x-3">
            <Checkbox v-model="safetyChecks.copingPlan" />
            <span class="text-sm text-gray-700">I want to create a safety plan</span>
          </label>
        </div>
      </div>
      
      <!-- Continue Option -->
      <div class="mt-6 pt-4 border-t border-gray-200">
        <Button 
          variant="ghost" 
          size="sm" 
          class="w-full"
          @click="continueChatWithSupport"
        >
          Continue our conversation with enhanced support
        </Button>
      </div>
    </div>
  </div>
</template>
```

### 7. Advanced Personalization Features

#### User Preference Dashboard
```vue
<template>
  <div class="personalization-dashboard">
    <!-- Preference Categories -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Communication Style -->
      <Card class="p-6">
        <CardHeader class="pb-4">
          <CardTitle class="flex items-center space-x-2">
            <MessageSquare class="w-5 h-5 text-[#4A90E2]" />
            <span>Communication Style</span>
          </CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="space-y-3">
            <label class="flex items-center space-x-3">
              <input 
                type="radio" 
                v-model="preferences.communicationStyle" 
                value="supportive"
                class="text-[#4A90E2] focus:ring-[#4A90E2]"
              />
              <div>
                <div class="font-medium">Supportive & Encouraging</div>
                <div class="text-sm text-gray-600">Warm, empathetic responses</div>
              </div>
            </label>
            <label class="flex items-center space-x-3">
              <input 
                type="radio" 
                v-model="preferences.communicationStyle" 
                value="direct"
                class="text-[#4A90E2] focus:ring-[#4A90E2]"
              />
              <div>
                <div class="font-medium">Direct & Practical</div>
                <div class="text-sm text-gray-600">Clear, solution-focused</div>
              </div>
            </label>
            <label class="flex items-center space-x-3">
              <input 
                type="radio" 
                v-model="preferences.communicationStyle" 
                value="analytical"
                class="text-[#4A90E2] focus:ring-[#4A90E2]"
              />
              <div>
                <div class="font-medium">Analytical & Detailed</div>
                <div class="text-sm text-gray-600">In-depth explanations</div>
              </div>
            </label>
          </div>
        </CardContent>
      </Card>
      
      <!-- Session Preferences -->
      <Card class="p-6">
        <CardHeader class="pb-4">
          <CardTitle class="flex items-center space-x-2">
            <Clock class="w-5 h-5 text-[#4A90E2]" />
            <span>Session Preferences</span>
          </CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Preferred session length
            </label>
            <Select v-model="preferences.sessionLength">
              <SelectTrigger>
                <SelectValue placeholder="Select duration" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="15">15 minutes</SelectItem>
                <SelectItem value="30">30 minutes</SelectItem>
                <SelectItem value="45">45 minutes</SelectItem>
                <SelectItem value="60">1 hour</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Reminder frequency
            </label>
            <Select v-model="preferences.reminderFrequency">
              <SelectTrigger>
                <SelectValue placeholder="Select frequency" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="biweekly">Bi-weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
                <SelectItem value="none">No reminders</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
      
      <!-- Privacy Settings -->
      <Card class="p-6">
        <CardHeader class="pb-4">
          <CardTitle class="flex items-center space-x-2">
            <Shield class="w-5 h-5 text-[#4A90E2]" />
            <span>Privacy & Data</span>
          </CardTitle>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="space-y-3">
            <label class="flex items-center justify-between">
              <div>
                <div class="font-medium">Save conversation history</div>
                <div class="text-sm text-gray-600">For progress tracking</div>
              </div>
              <Switch v-model="preferences.saveHistory" />
            </label>
            
            <label class="flex items-center justify-between">
              <div>
                <div class="font-medium">Anonymous usage analytics</div>
                <div class="text-sm text-gray-600">Help improve the service</div>
              </div>
              <Switch v-model="preferences.analytics" />
            </label>
            
            <label class="flex items-center justify-between">
              <div>
                <div class="font-medium">Personalized recommendations</div>
                <div class="text-sm text-gray-600">Based on your interactions</div>
              </div>
              <Switch v-model="preferences.personalization" />
            </label>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>
```
- **Next Steps**: Clear action items

### 5. Multi-language Experience

#### Language Detection
- **Automatic Detection**: Based on user input
- **Manual Override**: Easy language switching
- **Mixed Language Support**: Handling code-switching
- **Cultural Adaptation**: Context-appropriate responses

#### Translation Interface
- **Seamless Switching**: No page reloads
- **Content Preservation**: Maintain conversation context
- **Visual Indicators**: Current language clearly shown
- **Fallback Handling**: Graceful degradation

## Mobile-First Design

### Mobile Optimization Principles

#### Touch-First Interactions
- **Minimum Touch Targets**: 44px × 44px
- **Gesture Support**: Swipe, pinch, long-press
- **Thumb-Friendly Layout**: Important actions within reach
- **Haptic Feedback**: Tactile response for actions

#### Screen Size Adaptations
- **Responsive Breakpoints**:
  - Mobile: 320px - 768px
  - Tablet: 768px - 1024px
  - Desktop: 1024px+
- **Content Prioritization**: Most important content first
- **Progressive Disclosure**: Reveal information as needed

#### Mobile-Specific Features
- **Voice Input**: Prominent microphone button
- **Keyboard Optimization**: Appropriate input types
- **Offline Support**: Basic functionality without connection
- **App-like Experience**: PWA capabilities

### Mobile Interface Components

#### Mobile Chat Interface
- **Full-Screen Chat**: Maximize conversation area
- **Floating Action Button**: Quick access to voice input
- **Swipe Gestures**: Navigate between sections
- **Pull-to-Refresh**: Update conversation history

#### Mobile Navigation
- **Bottom Tab Bar**: Primary navigation
- **Hamburger Menu**: Secondary options
- **Breadcrumbs**: Clear navigation path
- **Back Button**: Consistent navigation behavior

## Accessibility Guidelines

### WCAG 2.1 AA Compliance

#### Visual Accessibility
- **Color Contrast**: Minimum 4.5:1 ratio for normal text
- **Color Independence**: Information not conveyed by color alone
- **Text Scaling**: Support up to 200% zoom
- **Focus Indicators**: Clear, visible focus states

#### Motor Accessibility
- **Keyboard Navigation**: Full functionality via keyboard
- **Click Targets**: Minimum 44px × 44px
- **Timeout Extensions**: User control over time limits
- **Motion Sensitivity**: Reduced motion options

#### Cognitive Accessibility
- **Clear Language**: Simple, jargon-free communication
- **Consistent Navigation**: Predictable interface patterns
- **Error Prevention**: Clear validation and guidance
- **Help Documentation**: Contextual assistance

### Assistive Technology Support

#### Screen Reader Compatibility
- **Semantic HTML**: Proper heading structure
- **ARIA Labels**: Descriptive labels for interactive elements
- **Live Regions**: Dynamic content announcements
- **Skip Links**: Quick navigation options

#### Voice Control Support
- **Voice Commands**: "Start chat", "Send message", "Read last response"
- **Speech Recognition**: Web Speech API integration
- **Voice Feedback**: Text-to-speech for responses
- **Command Shortcuts**: Efficient voice navigation

#### High Contrast Mode
- **System Integration**: Respect OS high contrast settings
- **Manual Toggle**: User-controlled high contrast option
- **Enhanced Borders**: Increased border visibility
- **Icon Alternatives**: Text labels for all icons

## Speech and Voice Interface

### Voice Input Design

#### Microphone Interface
- **Visual Feedback**: Animated microphone icon during recording
- **Audio Levels**: Visual representation of input volume
- **Recording States**: Clear start/stop/pause indicators
- **Error Handling**: Clear feedback for recognition failures

#### Speech Recognition UX
- **Continuous Listening**: Hands-free conversation mode
- **Push-to-Talk**: Manual control option
- **Noise Handling**: Background noise filtering
- **Accent Support**: Multi-accent recognition

### Voice Output Design

#### Text-to-Speech
- **Natural Voices**: Human-like speech synthesis
- **Speed Control**: User-adjustable playback speed
- **Pause/Resume**: User control over audio playback
- **Visual Sync**: Highlight text being spoken

#### Audio Feedback
- **Confirmation Sounds**: Subtle audio cues for actions
- **Error Sounds**: Distinct audio for errors
- **Notification Sounds**: Gentle alerts for new messages
- **Volume Control**: User-adjustable audio levels

## Emotional Design Elements

### Emotion Detection Interface

#### Visual Emotion Indicators
- **Emoji Representations**: Subtle emotion display
- **Color Coding**: Gentle color changes based on mood
- **Animation**: Smooth transitions between emotional states
- **User Control**: Option to hide emotion indicators

#### Empathetic Responses
- **Contextual Messaging**: Responses adapted to detected emotion
- **Supportive Language**: Encouraging, non-judgmental tone
- **Resource Suggestions**: Emotion-appropriate recommendations
- **Crisis Sensitivity**: Immediate support for distress

### Calming Design Elements

#### Visual Calm
- **Soft Animations**: Gentle, non-jarring transitions
- **Breathing Patterns**: Subtle pulsing animations
- **Nature Imagery**: Optional calming background elements
- **Minimalist Layout**: Reduced visual clutter

#### Interactive Calm
- **Smooth Scrolling**: Fluid page transitions
- **Gentle Haptics**: Subtle tactile feedback
- **Progressive Loading**: Smooth content appearance
- **Stress-Free Navigation**: Intuitive, predictable interactions

## Data Visualization & Progress Tracking

### Assessment Progress

#### Progress Indicators
- **Linear Progress Bar**: Clear completion percentage
- **Step Indicators**: Current question in sequence
- **Time Estimates**: Remaining time display
- **Completion Celebration**: Positive reinforcement

#### Results Visualization
- **Simple Charts**: Easy-to-understand data representation
- **Color-Coded Results**: Intuitive color schemes
- **Trend Indicators**: Progress over time
- **Comparison Views**: Before/after assessments

### Conversation Analytics

#### Chat History
- **Timeline View**: Chronological conversation display
- **Search Functionality**: Find specific topics or dates
- **Export Options**: PDF, text, or email export
- **Privacy Controls**: User-controlled data retention

#### Mood Tracking
- **Daily Check-ins**: Simple mood logging
- **Trend Visualization**: Mood patterns over time
- **Trigger Identification**: Pattern recognition insights
- **Goal Setting**: Personal wellness objectives

## Error States & Feedback

### Error Handling Design

#### Connection Errors
- **Offline Indicators**: Clear connection status
- **Retry Mechanisms**: Easy reconnection options
- **Cached Content**: Available offline functionality
- **Graceful Degradation**: Reduced but functional experience

#### Input Validation
- **Real-time Validation**: Immediate feedback on input
- **Clear Error Messages**: Specific, actionable guidance
- **Visual Indicators**: Color and icon-based error states
- **Recovery Assistance**: Help users correct errors

### Success Feedback

#### Positive Reinforcement
- **Completion Celebrations**: Encouraging success messages
- **Progress Acknowledgment**: Recognition of user effort
- **Achievement Badges**: Milestone recognition
- **Gentle Animations**: Positive visual feedback

#### Action Confirmations
- **Save Confirmations**: Clear feedback for data persistence
- **Send Confirmations**: Message delivery acknowledgment
- **Setting Changes**: Immediate feedback for preference updates
- **Export Success**: Confirmation of data export completion

## Performance & Loading States

### Loading Design

#### Progressive Loading
- **Skeleton Screens**: Content placeholders during loading
- **Streaming Content**: Real-time content appearance
- **Priority Loading**: Critical content first
- **Background Loading**: Non-blocking data fetching

#### Performance Indicators
- **Typing Indicators**: AI response preparation
- **Processing Animations**: Assessment analysis feedback
- **Connection Status**: Real-time connectivity display
- **Sync Indicators**: Data synchronization status

### Optimization Strategies

#### Content Optimization
- **Image Compression**: Optimized visual assets
- **Lazy Loading**: On-demand content loading
- **Caching Strategy**: Intelligent content caching
- **Minification**: Reduced file sizes

#### User Experience Optimization
- **Perceived Performance**: Fast-feeling interactions
- **Preemptive Loading**: Anticipatory content fetching
- **Smooth Animations**: 60fps interaction animations
- **Responsive Feedback**: Immediate user action acknowledgment

## Privacy & Security UX

### Privacy Controls

#### Data Management
- **Clear Privacy Settings**: Easy-to-understand controls
- **Data Export**: User-controlled data portability
- **Data Deletion**: Simple account and data removal
- **Consent Management**: Granular permission controls

#### Transparency Features
- **Data Usage Indicators**: Clear data collection notices
- **Privacy Dashboard**: Comprehensive privacy overview
- **Audit Logs**: User-accessible activity history
- **Third-party Disclosure**: Clear external data sharing notices

### Security Feedback

#### Authentication UX
- **Secure Login**: Clear security indicators
- **Session Management**: Visible session status
- **Two-Factor Authentication**: User-friendly 2FA setup
- **Password Security**: Strength indicators and guidance

#### Trust Indicators
- **Security Badges**: Visible security certifications
- **Encryption Notices**: Clear data protection indicators
- **Compliance Information**: HIPAA, GDPR compliance display
- **Professional Credentials**: Mental health professional verification

## Future UX Considerations

### Emerging Technologies

#### AI Enhancement
- **Predictive Interface**: AI-driven interface adaptation
- **Personalized Layouts**: User preference learning
- **Contextual Suggestions**: Smart recommendation system
- **Emotional AI**: Advanced emotion recognition

#### Extended Reality
- **VR Therapy Spaces**: Immersive therapeutic environments
- **AR Mood Tracking**: Augmented reality mood visualization
- **Mixed Reality Support**: Hybrid digital-physical experiences
- **Spatial Audio**: 3D audio for immersive experiences

### Advanced Personalization

#### Adaptive Interfaces
- **Learning Algorithms**: Interface optimization based on usage
- **Accessibility Adaptation**: Automatic accessibility adjustments
- **Cultural Customization**: Region-specific interface adaptations
- **Temporal Adaptation**: Time-of-day interface modifications

#### Predictive UX
- **Proactive Support**: Anticipatory mental health interventions
- **Smart Scheduling**: AI-driven appointment suggestions
- **Resource Prediction**: Personalized resource recommendations
- **Crisis Prevention**: Early warning system integration

## Implementation Guidelines

### Development Standards

#### Shadcn Vue Integration
```bash
# Install Shadcn Vue
npm install @shadcn/vue
npm install @vueuse/core
npm install class-variance-authority
npm install clsx
npm install tailwind-merge

# Initialize Shadcn Vue
npx shadcn-vue@latest init

# Add required components
npx shadcn-vue@latest add button
npx shadcn-vue@latest add input
npx shadcn-vue@latest add textarea
npx shadcn-vue@latest add card
npx shadcn-vue@latest add badge
npx shadcn-vue@latest add progress
npx shadcn-vue@latest add select
npx shadcn-vue@latest add switch
npx shadcn-vue@latest add checkbox
npx shadcn-vue@latest add dropdown-menu
npx shadcn-vue@latest add avatar
npx shadcn-vue@latest add alert
```

#### Code Quality Standards
- **Vue 3 Composition API**: Use `<script setup>` syntax consistently
- **TypeScript Integration**: Implement strict type checking
- **Shadcn Vue Components**: Use design system components exclusively
- **Error Boundaries**: Implement proper error handling
- **Accessibility First**: WCAG 2.1 AA compliance mandatory
- **Semantic HTML**: Use proper HTML5 semantic elements
- **ARIA Implementation**: Comprehensive ARIA labels and roles

#### Performance Optimization
- **Lazy Loading**: Use `defineAsyncComponent` for non-critical components
- **Virtual Scrolling**: Implement for large message lists
- **Memoization**: Use `v-memo` for expensive computations
- **Bundle Optimization**: Tree shaking and code splitting
- **Caching Strategy**: Implement intelligent caching
- **Web Workers**: Use for heavy computational tasks

#### Testing Strategy
- **Unit Testing**: Vitest for all components
- **Integration Testing**: User flow validation
- **Accessibility Testing**: @axe-core/vue integration
- **Visual Regression**: Automated UI testing
- **Performance Testing**: Lighthouse CI integration
- **E2E Testing**: Playwright for critical paths

### Quality Assurance

#### Review Checklist
- [ ] **Shadcn Vue Compliance**: Components used correctly
- [ ] **Accessibility Standards**: WCAG 2.1 AA met
- [ ] **Mobile Responsiveness**: All breakpoints tested
- [ ] **Performance Benchmarks**: Core Web Vitals optimized
- [ ] **Error Handling**: Graceful error states
- [ ] **Loading States**: Proper loading indicators
- [ ] **Crisis Detection**: Safety features functional
- [ ] **Privacy Compliance**: Data protection verified
- [ ] **Multi-language**: Internationalization working
- [ ] **Cross-browser**: Compatibility verified

#### Deployment Standards
- **Environment Configuration**: Proper env management
- **Progressive Web App**: PWA features enabled
- **Service Worker**: Offline functionality
- **CDN Optimization**: Static asset delivery
- **Security Headers**: Comprehensive security setup
- **Analytics Integration**: User behavior tracking
- **Monitoring Setup**: Real-time performance monitoring

#### Continuous Improvement
- **User Analytics**: Behavior tracking and analysis
- **A/B Testing**: Feature experimentation framework
- **Feedback Collection**: Systematic user input gathering
- **Performance Monitoring**: Real-time UX metrics
- **Accessibility Audits**: Regular compliance testing
- **Security Reviews**: Ongoing security assessments

## 13. Fully Interactive Chat with Seamless Animations

### Animation Library Integration

#### VueUse Motion Setup
```bash
# Install VueUse Motion for Vue 3
npm install @vueuse/motion

# Install Motion Primitives CLI (for React components reference)
npx motion-primitives list
npx motion add text-effect
npx motion add animated-group
npx motion add transition-panel
```

#### Vue Motion Configuration
```typescript
// main.ts
import { createApp } from 'vue'
import { MotionPlugin } from '@vueuse/motion'
import App from './App.vue'

const app = createApp(App)
app.use(MotionPlugin)
app.mount('#app')
```

### Animated Chat Interface Components

#### Real-time Chat Container with Smooth Animations
```vue
<template>
  <div class="chat-container h-full flex flex-col bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
    <!-- Chat Header with Slide Animation -->
    <div 
      class="chat-header p-4 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700"
      v-motion-slide-visible-once-top
      :delay="100"
    >
      <div class="flex items-center space-x-3">
        <Avatar class="h-10 w-10" v-motion-pop-visible-once :delay="200">
          <AvatarImage src="/ai-therapist-avatar.svg" alt="AI Therapist" />
          <AvatarFallback>AI</AvatarFallback>
        </Avatar>
        <div class="flex-1" v-motion-fade-visible-once :delay="300">
          <h3 class="font-semibold text-gray-900 dark:text-white">Mental Health Assistant</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400 flex items-center">
            <div class="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
            Online & Ready to Help
          </p>
        </div>
        <Button variant="ghost" size="sm" v-motion-scale-visible-once :delay="400">
          <MoreVertical class="h-4 w-4" />
        </Button>
      </div>
    </div>

    <!-- Messages Area with Staggered Animation -->
    <ScrollArea class="flex-1 p-4" ref="messagesContainer">
      <div class="space-y-4">
        <TransitionGroup
          name="message"
          tag="div"
          @enter="onMessageEnter"
          @leave="onMessageLeave"
        >
          <div
            v-for="(message, index) in messages"
            :key="message.id"
            :class="[
              'message-item flex',
              message.sender === 'user' ? 'justify-end' : 'justify-start'
            ]"
            v-motion-slide-visible-once-bottom
            :delay="index * 100"
          >
            <!-- AI Message Bubble -->
            <div
              v-if="message.sender === 'ai'"
              class="max-w-xs lg:max-w-md"
              v-motion-fade-visible-once
              :delay="index * 150"
            >
              <div class="flex items-start space-x-2">
                <Avatar class="h-8 w-8 mt-1" v-motion-pop-visible-once :delay="index * 200">
                  <AvatarImage src="/ai-therapist-avatar.svg" alt="AI" />
                  <AvatarFallback>AI</AvatarFallback>
                </Avatar>
                <div class="bg-white dark:bg-gray-700 rounded-2xl rounded-tl-md p-3 shadow-sm border border-gray-200 dark:border-gray-600">
                  <TypewriterText 
                    :text="message.content" 
                    :speed="30"
                    class="text-gray-800 dark:text-gray-200"
                  />
                  <div class="flex items-center justify-between mt-2">
                    <span class="text-xs text-gray-500 dark:text-gray-400">{{ formatTime(message.timestamp) }}</span>
                    <div class="flex space-x-1" v-motion-fade-visible-once :delay="index * 300">
                      <Button variant="ghost" size="sm" @click="likeMessage(message.id)">
                        <ThumbsUp class="h-3 w-3" :class="{ 'text-blue-500': message.liked }" />
                      </Button>
                      <Button variant="ghost" size="sm" @click="copyMessage(message.content)">
                        <Copy class="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- User Message Bubble -->
            <div
              v-else
              class="max-w-xs lg:max-w-md"
              v-motion-slide-visible-once-right
              :delay="index * 100"
            >
              <div class="bg-blue-500 text-white rounded-2xl rounded-tr-md p-3 shadow-sm">
                <p class="text-sm">{{ message.content }}</p>
                <div class="flex items-center justify-between mt-2">
                  <span class="text-xs text-blue-100">{{ formatTime(message.timestamp) }}</span>
                  <div class="flex items-center space-x-1">
                    <Check class="h-3 w-3 text-blue-200" v-if="message.status === 'sent'" />
                    <CheckCheck class="h-3 w-3 text-blue-200" v-if="message.status === 'delivered'" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </TransitionGroup>

        <!-- Typing Indicator -->
        <div 
          v-if="isTyping" 
          class="flex justify-start"
          v-motion-fade-visible-once
        >
          <div class="flex items-start space-x-2">
            <Avatar class="h-8 w-8 mt-1">
              <AvatarImage src="/ai-therapist-avatar.svg" alt="AI" />
              <AvatarFallback>AI</AvatarFallback>
            </Avatar>
            <div class="bg-white dark:bg-gray-700 rounded-2xl rounded-tl-md p-3 shadow-sm border border-gray-200 dark:border-gray-600">
              <TypingIndicator />
            </div>
          </div>
        </div>
      </div>
    </ScrollArea>

    <!-- Quick Response Suggestions -->
    <div 
      v-if="quickResponses.length > 0" 
      class="px-4 py-2"
      v-motion-slide-visible-once-bottom
      :delay="200"
    >
      <div class="flex flex-wrap gap-2">
        <Button
          v-for="(response, index) in quickResponses"
          :key="response.id"
          variant="outline"
          size="sm"
          @click="sendQuickResponse(response.text)"
          class="text-xs hover:scale-105 transition-transform"
          v-motion-pop-visible-once
          :delay="index * 100"
        >
          {{ response.text }}
        </Button>
      </div>
    </div>

    <!-- Input Area with Smooth Animations -->
    <div 
      class="chat-input p-4 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-t border-gray-200 dark:border-gray-700"
      v-motion-slide-visible-once-bottom
      :delay="300"
    >
      <div class="flex items-end space-x-2">
        <div class="flex-1 relative">
          <Textarea
            v-model="newMessage"
            placeholder="Share what's on your mind..."
            class="min-h-[44px] max-h-32 resize-none pr-12 rounded-2xl border-gray-300 dark:border-gray-600 focus:border-blue-500 dark:focus:border-blue-400"
            @keydown.enter.prevent="handleEnterKey"
            @input="handleTyping"
            ref="messageInput"
          />
          <Button
            variant="ghost"
            size="sm"
            class="absolute right-2 bottom-2 h-8 w-8 p-0"
            @click="toggleEmojiPicker"
            v-motion-scale-visible-once
            :delay="400"
          >
            <Smile class="h-4 w-4" />
          </Button>
        </div>
        <Button
          @click="sendMessage"
          :disabled="!newMessage.trim() || isSending"
          class="h-11 w-11 rounded-full p-0 transition-all duration-200"
          :class="{
            'scale-110 shadow-lg': newMessage.trim(),
            'opacity-50': !newMessage.trim() || isSending
          }"
          v-motion-pop-visible-once
          :delay="500"
        >
          <Send class="h-4 w-4" v-if="!isSending" />
          <Loader2 class="h-4 w-4 animate-spin" v-else />
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { 
  Send, 
  Smile, 
  MoreVertical, 
  ThumbsUp, 
  Copy, 
  Check, 
  CheckCheck, 
  Loader2 
} from 'lucide-vue-next'

interface Message {
  id: string
  content: string
  sender: 'user' | 'ai'
  timestamp: Date
  status?: 'sending' | 'sent' | 'delivered'
  liked?: boolean
}

interface QuickResponse {
  id: string
  text: string
  category: string
}

const messages = ref<Message[]>([])
const newMessage = ref('')
const isTyping = ref(false)
const isSending = ref(false)
const messagesContainer = ref()
const messageInput = ref()

const quickResponses = ref<QuickResponse[]>([
  { id: '1', text: "I'm feeling anxious", category: 'emotion' },
  { id: '2', text: "I need coping strategies", category: 'help' },
  { id: '3', text: "Tell me about mindfulness", category: 'learn' },
  { id: '4', text: "I'm having trouble sleeping", category: 'issue' }
])

const sendMessage = async () => {
  if (!newMessage.value.trim() || isSending.value) return

  const userMessage: Message = {
    id: Date.now().toString(),
    content: newMessage.value,
    sender: 'user',
    timestamp: new Date(),
    status: 'sending'
  }

  messages.value.push(userMessage)
  newMessage.value = ''
  isSending.value = true

  await nextTick()
  scrollToBottom()

  // Simulate AI response
  setTimeout(() => {
    userMessage.status = 'delivered'
    isTyping.value = true
    
    setTimeout(() => {
      isTyping.value = false
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: generateAIResponse(userMessage.content),
        sender: 'ai',
        timestamp: new Date()
      }
      messages.value.push(aiResponse)
      scrollToBottom()
      isSending.value = false
    }, 2000)
  }, 500)
}

const sendQuickResponse = (text: string) => {
  newMessage.value = text
  sendMessage()
}

const handleEnterKey = (event: KeyboardEvent) => {
  if (!event.shiftKey) {
    sendMessage()
  }
}

const handleTyping = () => {
  // Implement typing indicator logic
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      const scrollElement = messagesContainer.value.$el.querySelector('[data-radix-scroll-area-viewport]')
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight
      }
    }
  })
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const generateAIResponse = (userInput: string): string => {
  // Simple AI response generation (replace with actual AI integration)
  const responses = [
    "I understand how you're feeling. Let's explore this together.",
    "Thank you for sharing that with me. Can you tell me more about what's been on your mind?",
    "It sounds like you're going through a challenging time. I'm here to support you.",
    "That's a very valid concern. Let's work through some strategies that might help."
  ]
  return responses[Math.floor(Math.random() * responses.length)]
}

const likeMessage = (messageId: string) => {
  const message = messages.value.find(m => m.id === messageId)
  if (message) {
    message.liked = !message.liked
  }
}

const copyMessage = (content: string) => {
  navigator.clipboard.writeText(content)
}

const toggleEmojiPicker = () => {
  // Implement emoji picker
}

const onMessageEnter = (el: Element) => {
  // Custom enter animation
}

const onMessageLeave = (el: Element) => {
  // Custom leave animation
}

onMounted(() => {
  // Initialize with welcome message
  messages.value.push({
    id: '0',
    content: "Hello! I'm here to support your mental health journey. How are you feeling today?",
    sender: 'ai',
    timestamp: new Date()
  })
})
</script>

<style scoped>
.message-enter-active {
  transition: all 0.3s ease-out;
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

.chat-container {
  height: calc(100vh - 4rem);
}
</style>
```

#### Typewriter Text Effect Component
```vue
<template>
  <span ref="textElement">{{ displayText }}</span>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

interface Props {
  text: string
  speed?: number
  delay?: number
}

const props = withDefaults(defineProps<Props>(), {
  speed: 50,
  delay: 0
})

const displayText = ref('')
const textElement = ref<HTMLElement>()

const typeText = async () => {
  displayText.value = ''
  
  if (props.delay > 0) {
    await new Promise(resolve => setTimeout(resolve, props.delay))
  }

  for (let i = 0; i <= props.text.length; i++) {
    displayText.value = props.text.slice(0, i)
    await new Promise(resolve => setTimeout(resolve, props.speed))
  }
}

watch(() => props.text, () => {
  typeText()
}, { immediate: true })

onMounted(() => {
  typeText()
})
</script>
```

#### Typing Indicator Component
```vue
<template>
  <div class="flex items-center space-x-1">
    <div class="text-sm text-gray-500 dark:text-gray-400 mr-2">AI is typing</div>
    <div class="flex space-x-1">
      <div 
        v-for="i in 3" 
        :key="i"
        class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"
        :style="{ animationDelay: `${(i - 1) * 0.2}s` }"
      ></div>
    </div>
  </div>
</template>
```

### Advanced Animation Features

#### Emotion-Based Message Animations
```vue
<template>
  <div 
    :class="[
      'message-bubble p-3 rounded-2xl transition-all duration-300',
      emotionClasses[emotion]
    ]"
    v-motion
    :initial="{ scale: 0.8, opacity: 0 }"
    :enter="{ 
      scale: 1, 
      opacity: 1,
      transition: { 
        type: 'spring',
        stiffness: 300,
        damping: 20
      }
    }"
    :hover="{
      scale: 1.02,
      transition: { duration: 0.2 }
    }"
  >
    <div class="flex items-start space-x-2">
      <div 
        class="emotion-indicator w-3 h-3 rounded-full"
        :class="emotionIndicatorClasses[emotion]"
        v-motion-pop-visible-once
        :delay="200"
      ></div>
      <p class="text-sm">{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  message: string
  emotion: 'positive' | 'negative' | 'neutral' | 'crisis'
}

const props = defineProps<Props>()

const emotionClasses = {
  positive: 'bg-green-100 dark:bg-green-900/30 border-green-200 dark:border-green-700',
  negative: 'bg-red-100 dark:bg-red-900/30 border-red-200 dark:border-red-700',
  neutral: 'bg-gray-100 dark:bg-gray-700 border-gray-200 dark:border-gray-600',
  crisis: 'bg-orange-100 dark:bg-orange-900/30 border-orange-200 dark:border-orange-700 ring-2 ring-orange-300'
}

const emotionIndicatorClasses = {
  positive: 'bg-green-500 animate-pulse',
  negative: 'bg-red-500 animate-pulse',
  neutral: 'bg-gray-400',
  crisis: 'bg-orange-500 animate-ping'
}
</script>
```

#### Interactive Assessment Cards with Smooth Transitions
```vue
<template>
  <div class="assessment-container space-y-4">
    <TransitionGroup
      name="assessment"
      tag="div"
      class="space-y-4"
    >
      <Card
        v-for="(question, index) in questions"
        :key="question.id"
        v-show="currentQuestionIndex >= index"
        class="assessment-card"
        v-motion-slide-visible-once-right
        :delay="index * 200"
      >
        <CardHeader>
          <div class="flex items-center justify-between">
            <CardTitle class="text-lg">{{ question.title }}</CardTitle>
            <Badge variant="outline" v-motion-fade-visible-once :delay="index * 300">
              {{ index + 1 }} / {{ questions.length }}
            </Badge>
          </div>
          <Progress 
            :value="((index + 1) / questions.length) * 100" 
            class="w-full"
            v-motion-slide-visible-once-right
            :delay="index * 400"
          />
        </CardHeader>
        <CardContent>
          <p class="text-gray-600 dark:text-gray-300 mb-4" v-motion-fade-visible-once :delay="index * 500">
            {{ question.description }}
          </p>
          
          <!-- Likert Scale with Animated Options -->
          <div v-if="question.type === 'likert'" class="space-y-3">
            <div class="grid grid-cols-5 gap-2">
              <Button
                v-for="(option, optionIndex) in question.options"
                :key="optionIndex"
                :variant="selectedAnswers[question.id] === optionIndex ? 'default' : 'outline'"
                @click="selectAnswer(question.id, optionIndex)"
                class="h-12 text-xs transition-all duration-200 hover:scale-105"
                v-motion-pop-visible-once
                :delay="index * 600 + optionIndex * 100"
              >
                {{ option.label }}
              </Button>
            </div>
            <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400">
              <span v-motion-fade-visible-once :delay="index * 700">{{ question.scaleLabels.min }}</span>
              <span v-motion-fade-visible-once :delay="index * 750">{{ question.scaleLabels.max }}</span>
            </div>
          </div>

          <!-- Visual Mood Selector -->
          <div v-else-if="question.type === 'mood'" class="grid grid-cols-5 gap-3">
            <Button
              v-for="(mood, moodIndex) in moodOptions"
              :key="moodIndex"
              :variant="selectedAnswers[question.id] === moodIndex ? 'default' : 'outline'"
              @click="selectAnswer(question.id, moodIndex)"
              class="h-16 flex flex-col items-center justify-center transition-all duration-200 hover:scale-110"
              v-motion-pop-visible-once
              :delay="index * 600 + moodIndex * 150"
            >
              <span class="text-2xl mb-1">{{ mood.emoji }}</span>
              <span class="text-xs">{{ mood.label }}</span>
            </Button>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-between mt-6">
            <Button
              v-if="index > 0"
              variant="outline"
              @click="previousQuestion"
              v-motion-slide-visible-once-left
              :delay="index * 800"
            >
              Previous
            </Button>
            <div v-else></div>
            
            <Button
              @click="nextQuestion"
              :disabled="!selectedAnswers[question.id]"
              v-motion-slide-visible-once-right
              :delay="index * 850"
            >
              {{ index === questions.length - 1 ? 'Complete' : 'Next' }}
            </Button>
          </div>
        </CardContent>
      </Card>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'

interface AssessmentQuestion {
  id: string
  title: string
  description: string
  type: 'likert' | 'mood' | 'slider'
  options?: { label: string; value: number }[]
  scaleLabels?: { min: string; max: string }
}

const currentQuestionIndex = ref(0)
const selectedAnswers = ref<Record<string, number>>({})

const questions = ref<AssessmentQuestion[]>([
  {
    id: 'anxiety-level',
    title: 'How anxious have you been feeling lately?',
    description: 'Rate your overall anxiety level over the past week.',
    type: 'likert',
    options: [
      { label: 'Not at all', value: 1 },
      { label: 'Slightly', value: 2 },
      { label: 'Moderately', value: 3 },
      { label: 'Very', value: 4 },
      { label: 'Extremely', value: 5 }
    ],
    scaleLabels: { min: 'Not anxious', max: 'Very anxious' }
  },
  {
    id: 'current-mood',
    title: 'How would you describe your mood right now?',
    description: 'Select the emoji that best represents how you\'re feeling.',
    type: 'mood'
  }
])

const moodOptions = [
  { emoji: '😊', label: 'Happy', value: 5 },
  { emoji: '🙂', label: 'Good', value: 4 },
  { emoji: '😐', label: 'Neutral', value: 3 },
  { emoji: '😔', label: 'Sad', value: 2 },
  { emoji: '😢', label: 'Very Sad', value: 1 }
]

const selectAnswer = (questionId: string, value: number) => {
  selectedAnswers.value[questionId] = value
}

const nextQuestion = () => {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++
  } else {
    // Complete assessment
    console.log('Assessment completed:', selectedAnswers.value)
  }
}

const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  }
}
</script>

<style scoped>
.assessment-enter-active {
  transition: all 0.5s ease-out;
}

.assessment-leave-active {
  transition: all 0.3s ease-in;
}

.assessment-enter-from {
  opacity: 0;
  transform: translateX(50px) scale(0.95);
}

.assessment-leave-to {
  opacity: 0;
  transform: translateX(-50px) scale(0.95);
}
</style>
```

### Performance Optimization for Animations

#### Lazy Loading Animation Components
```typescript
// composables/useAnimations.ts
import { defineAsyncComponent } from 'vue'

export const useAnimationComponents = () => {
  const TypewriterText = defineAsyncComponent(() => import('@/components/animations/TypewriterText.vue'))
  const TypingIndicator = defineAsyncComponent(() => import('@/components/animations/TypingIndicator.vue'))
  const EmotionBubble = defineAsyncComponent(() => import('@/components/animations/EmotionBubble.vue'))
  
  return {
    TypewriterText,
    TypingIndicator,
    EmotionBubble
  }
}
```

#### Animation Performance Configuration
```typescript
// utils/animationConfig.ts
export const animationConfig = {
  // Reduce animations on low-end devices
  reducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  
  // Performance-optimized animation settings
  defaultTransition: {
    type: 'spring',
    stiffness: 300,
    damping: 30,
    mass: 0.8
  },
  
  // Stagger delays for better performance
  staggerDelay: 100,
  
  // Animation durations
  durations: {
    fast: 200,
    normal: 300,
    slow: 500
  }
}

// Utility function to get optimized animation props
export const getAnimationProps = (type: 'fast' | 'normal' | 'slow' = 'normal') => {
  if (animationConfig.reducedMotion) {
    return {
      initial: { opacity: 1 },
      enter: { opacity: 1 },
      transition: { duration: 0 }
    }
  }
  
  return {
    initial: { opacity: 0, y: 20 },
    enter: { 
      opacity: 1, 
      y: 0,
      transition: {
        ...animationConfig.defaultTransition,
        duration: animationConfig.durations[type]
      }
    }
  }
}
```

---

*This comprehensive UI/UX documentation provides the foundation for building an exceptional mental health chatbot experience using Shadcn Vue components, with focus on accessibility, performance, and user-centered design principles. The implementation emphasizes seamless user interaction, intelligent conversation flows, crisis support integration, advanced personalization features, and fully interactive chat with seamless animations powered by VueUse Motion and Motion Primitives concepts.*