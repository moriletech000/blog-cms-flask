#!/usr/bin/env python
"""
Standalone demo of Blog CMS
Shows the application structure without requiring PostgreSQL
"""

from flask import Flask, render_template_string, redirect, url_for
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'demo-secret-key'

# Sample data
posts = [
    {
        'id': 1,
        'title': 'Welcome to Blog CMS',
        'slug': 'welcome-to-blog-cms',
        'excerpt': 'A complete, production-ready blog management system built with Flask.',
        'author': 'Admin',
        'category': 'Technology',
        'date': datetime(2024, 1, 15),
        'views': 150,
        'likes': 12
    },
    {
        'id': 2,
        'title': 'Building Modern Web Applications',
        'slug': 'building-modern-web-apps',
        'excerpt': 'Learn how to build scalable web applications with Flask and PostgreSQL.',
        'author': 'Editor',
        'category': 'Web Development',
        'date': datetime(2024, 1, 20),
        'views': 89,
        'likes': 8
    },
    {
        'id': 3,
        'title': 'Python Tips and Tricks',
        'slug': 'python-tips-and-tricks',
        'excerpt': 'Improve your Python code with these essential tips and best practices.',
        'author': 'Admin',
        'category': 'Programming',
        'date': datetime(2024, 1, 25),
        'views': 234,
        'likes': 19
    }
]

# Homepage template
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Blog CMS - Demo</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 py-4">
            <div class="flex justify-between items-center">
                <h1 class="text-2xl font-bold text-gray-900">Blog CMS</h1>
                <div class="space-x-4">
                    <a href="/" class="text-gray-600 hover:text-gray-900">Home</a>
                    <a href="/admin-demo" class="text-gray-600 hover:text-gray-900">Admin Demo</a>
                    <a href="/api-demo" class="text-gray-600 hover:text-gray-900">API Demo</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <div class="bg-indigo-600 text-white py-12">
        <div class="max-w-7xl mx-auto px-4">
            <h2 class="text-4xl font-bold mb-4">Welcome to Blog CMS</h2>
            <p class="text-xl">A complete, production-ready blog management system built with Flask</p>
        </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 py-8">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Posts -->
            <div class="lg:col-span-2">
                <h3 class="text-2xl font-bold text-gray-900 mb-6">Latest Posts</h3>
                <div class="space-y-6">
                    {% for post in posts %}
                    <article class="bg-white rounded-lg shadow-sm border p-6 hover:shadow-md transition">
                        <div class="flex items-center mb-3">
                            <span class="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm font-medium">
                                {{ post.category }}
                            </span>
                        </div>
                        <h4 class="text-xl font-semibold text-gray-900 mb-2">
                            <a href="/post/{{ post.slug }}" class="hover:text-indigo-600">
                                {{ post.title }}
                            </a>
                        </h4>
                        <p class="text-gray-600 mb-4">{{ post.excerpt }}</p>
                        <div class="flex items-center justify-between text-sm text-gray-500">
                            <div class="flex items-center space-x-4">
                                <span>By {{ post.author }}</span>
                                <span>{{ post.date.strftime('%B %d, %Y') }}</span>
                            </div>
                            <div class="flex items-center space-x-3">
                                <span>{{ post.views }} views</span>
                                <span>{{ post.likes }} likes</span>
                            </div>
                        </div>
                    </article>
                    {% endfor %}
                </div>
            </div>

            <!-- Sidebar -->
            <div class="lg:col-span-1">
                <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
                    <h4 class="text-lg font-semibold text-gray-900 mb-4">About This Demo</h4>
                    <p class="text-gray-600 text-sm mb-4">
                        This is a simplified demo of the Blog CMS system. The full version includes:
                    </p>
                    <ul class="text-sm text-gray-600 space-y-2">
                        <li>✓ Multi-user authentication</li>
                        <li>✓ Rich text editor</li>
                        <li>✓ Comment system</li>
                        <li>✓ REST API</li>
                        <li>✓ Background tasks</li>
                        <li>✓ Image processing</li>
                        <li>✓ Full-text search</li>
                        <li>✓ Docker deployment</li>
                    </ul>
                </div>

                <div class="bg-indigo-50 rounded-lg border border-indigo-200 p-6">
                    <h4 class="text-lg font-semibold text-gray-900 mb-3">Full Version</h4>
                    <p class="text-sm text-gray-700 mb-4">
                        To run the complete system with all features:
                    </p>
                    <div class="bg-white rounded p-3 text-xs font-mono text-gray-800 mb-3">
                        docker compose up --build
                    </div>
                    <p class="text-xs text-gray-600">
                        See WINDOWS_SETUP.md for detailed instructions
                    </p>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="bg-white border-t mt-12 py-8">
        <div class="max-w-7xl mx-auto px-4 text-center text-gray-600">
            <p>Blog CMS - Production-Ready Flask Blog System</p>
            <p class="text-sm mt-2">Built with Flask, PostgreSQL, Redis, and Celery</p>
        </div>
    </footer>
</body>
</html>
'''

ADMIN_DEMO_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel - Blog CMS Demo</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 py-4">
            <div class="flex justify-between items-center">
                <h1 class="text-2xl font-bold text-gray-900">Blog CMS - Admin Panel</h1>
                <a href="/" class="text-indigo-600 hover:text-indigo-800">← Back to Blog</a>
            </div>
        </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 py-8">
        <h2 class="text-3xl font-bold text-gray-900 mb-8">Dashboard</h2>

        <!-- Stats -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow-sm border p-6">
                <div class="text-sm text-gray-600 mb-2">Total Posts</div>
                <div class="text-3xl font-bold text-gray-900">{{ posts|length }}</div>
                <div class="text-sm text-green-600 mt-2">↑ 12% from last month</div>
            </div>
            <div class="bg-white rounded-lg shadow-sm border p-6">
                <div class="text-sm text-gray-600 mb-2">Total Views</div>
                <div class="text-3xl font-bold text-gray-900">473</div>
                <div class="text-sm text-green-600 mt-2">↑ 8% from last month</div>
            </div>
            <div class="bg-white rounded-lg shadow-sm border p-6">
                <div class="text-sm text-gray-600 mb-2">Total Likes</div>
                <div class="text-3xl font-bold text-gray-900">39</div>
                <div class="text-sm text-green-600 mt-2">↑ 15% from last month</div>
            </div>
            <div class="bg-white rounded-lg shadow-sm border p-6">
                <div class="text-sm text-gray-600 mb-2">Active Users</div>
                <div class="text-3xl font-bold text-gray-900">5</div>
                <div class="text-sm text-gray-600 mt-2">2 admins, 3 editors</div>
            </div>
        </div>

        <!-- Recent Posts -->
        <div class="bg-white rounded-lg shadow-sm border p-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-4">Recent Posts</h3>
            <table class="w-full">
                <thead>
                    <tr class="border-b">
                        <th class="text-left py-3 px-4 text-sm font-medium text-gray-600">Title</th>
                        <th class="text-left py-3 px-4 text-sm font-medium text-gray-600">Author</th>
                        <th class="text-left py-3 px-4 text-sm font-medium text-gray-600">Category</th>
                        <th class="text-left py-3 px-4 text-sm font-medium text-gray-600">Views</th>
                        <th class="text-left py-3 px-4 text-sm font-medium text-gray-600">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for post in posts %}
                    <tr class="border-b hover:bg-gray-50">
                        <td class="py-3 px-4">{{ post.title }}</td>
                        <td class="py-3 px-4">{{ post.author }}</td>
                        <td class="py-3 px-4">{{ post.category }}</td>
                        <td class="py-3 px-4">{{ post.views }}</td>
                        <td class="py-3 px-4">
                            <span class="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
                                Published
                            </span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h4 class="font-semibold text-gray-900 mb-2">Full Admin Panel Features</h4>
            <p class="text-sm text-gray-700 mb-3">The complete admin panel includes:</p>
            <ul class="text-sm text-gray-700 space-y-1">
                <li>• Post creation with rich text editor</li>
                <li>• Image upload and management</li>
                <li>• User management and roles</li>
                <li>• Comment moderation</li>
                <li>• Category and tag management</li>
                <li>• Analytics and reporting</li>
            </ul>
        </div>
    </div>
</body>
</html>
'''

API_DEMO_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>API Demo - Blog CMS</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 py-4">
            <div class="flex justify-between items-center">
                <h1 class="text-2xl font-bold text-gray-900">Blog CMS - API Demo</h1>
                <a href="/" class="text-indigo-600 hover:text-indigo-800">← Back to Blog</a>
            </div>
        </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 py-8">
        <h2 class="text-3xl font-bold text-gray-900 mb-4">REST API</h2>
        <p class="text-gray-600 mb-8">The full system includes a complete REST API with JWT authentication</p>

        <div class="bg-white rounded-lg shadow-sm border p-6 mb-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-4">Sample API Response</h3>
            <div class="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                <pre class="text-green-400 text-sm font-mono">{{ api_response }}</pre>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-white rounded-lg shadow-sm border p-6">
                <h4 class="font-semibold text-gray-900 mb-3">Available Endpoints</h4>
                <ul class="text-sm text-gray-700 space-y-2 font-mono">
                    <li class="flex"><span class="text-green-600 w-16">GET</span> /api/v1/posts</li>
                    <li class="flex"><span class="text-blue-600 w-16">POST</span> /api/v1/posts</li>
                    <li class="flex"><span class="text-green-600 w-16">GET</span> /api/v1/posts/:slug</li>
                    <li class="flex"><span class="text-yellow-600 w-16">PUT</span> /api/v1/posts/:slug</li>
                    <li class="flex"><span class="text-red-600 w-16">DELETE</span> /api/v1/posts/:slug</li>
                    <li class="flex"><span class="text-green-600 w-16">GET</span> /api/v1/categories</li>
                    <li class="flex"><span class="text-green-600 w-16">GET</span> /api/v1/tags</li>
                    <li class="flex"><span class="text-blue-600 w-16">POST</span> /api/v1/auth/token</li>
                </ul>
            </div>

            <div class="bg-white rounded-lg shadow-sm border p-6">
                <h4 class="font-semibold text-gray-900 mb-3">Features</h4>
                <ul class="text-sm text-gray-700 space-y-2">
                    <li>✓ JWT Authentication</li>
                    <li>✓ Token Refresh</li>
                    <li>✓ Pagination</li>
                    <li>✓ Filtering & Search</li>
                    <li>✓ Auto-generated Swagger Docs</li>
                    <li>✓ Rate Limiting</li>
                    <li>✓ CORS Support</li>
                    <li>✓ Error Handling</li>
                </ul>
            </div>
        </div>

        <div class="mt-6 bg-indigo-50 border border-indigo-200 rounded-lg p-6">
            <h4 class="font-semibold text-gray-900 mb-2">Swagger Documentation</h4>
            <p class="text-sm text-gray-700 mb-3">
                The full system includes interactive API documentation at:
            </p>
            <div class="bg-white rounded p-3 text-sm font-mono text-gray-800">
                http://localhost/api/v1/docs
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE, posts=posts)

@app.route('/admin-demo')
def admin_demo():
    return render_template_string(ADMIN_DEMO_TEMPLATE, posts=posts)

@app.route('/api-demo')
def api_demo():
    import json
    api_response = json.dumps({
        "data": [
            {
                "id": "1",
                "title": "Welcome to Blog CMS",
                "slug": "welcome-to-blog-cms",
                "excerpt": "A complete, production-ready blog management system...",
                "author": {
                    "username": "admin",
                    "role": "admin"
                },
                "category": {
                    "name": "Technology",
                    "slug": "technology"
                },
                "tags": ["flask", "python"],
                "views": 150,
                "like_count": 12,
                "published_at": "2024-01-15T10:00:00"
            }
        ],
        "meta": {
            "page": 1,
            "per_page": 10,
            "total": 3,
            "pages": 1
        }
    }, indent=2)
    return render_template_string(API_DEMO_TEMPLATE, api_response=api_response)

@app.route('/post/<slug>')
def post_detail(slug):
    post = next((p for p in posts if p['slug'] == slug), None)
    if not post:
        return "Post not found", 404
    return redirect(url_for('home'))

if __name__ == '__main__':
    print("=" * 60)
    print("Blog CMS - Standalone Demo")
    print("=" * 60)
    print()
    print("🚀 Starting demo server...")
    print()
    print("Access the demo at:")
    print("  🌐 Homepage:    http://localhost:5000")
    print("  👤 Admin Demo:  http://localhost:5000/admin-demo")
    print("  📚 API Demo:    http://localhost:5000/api-demo")
    print()
    print("This is a simplified demo showing the UI and structure.")
    print("For the full system with all features, use Docker:")
    print("  docker compose up --build")
    print()
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)