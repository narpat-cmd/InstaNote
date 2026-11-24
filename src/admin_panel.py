"""Admin panel for InstaNote - Flask-based web dashboard."""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from functools import wraps

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_socketio import SocketIO, emit
import plotly.graph_objs as go
import plotly.utils

from src.config import get_config
from src.topic_selector import TopicSelector, VEHICLE_CATEGORIES
from src.scheduler import get_scheduler, InstaNoteScheduler, JobStatus
from src.content_generator import get_content_generator
from src.instagram_poster import get_instagram_poster
from src.utils import setup_logging, format_file_size, time_ago, slugify
from src.config import load_config, reload_config
import yaml


logger = logging.getLogger(__name__)


def create_app(config_path: Optional[str] = None) -> tuple:
    """Create Flask application with SocketIO."""
    config = get_config()

    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')
    app.config['SECRET_KEY'] = config.admin.secret_key
    app.config['SESSION_COOKIE_SECURE'] = False  # Set True for HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

    # Initialize components
    topic_selector = TopicSelector()
    scheduler = get_scheduler()
    content_generator = get_content_generator()
    instagram_poster = get_instagram_poster()

    # Authentication decorator
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('logged_in'):
                return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function

    # Routes
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            password = request.form.get('password', '')
            if password == config.admin.secret_key or password == os.environ.get('ADMIN_PASSWORD', ''):
                session['logged_in'] = True
                session['login_time'] = datetime.now().isoformat()
                next_url = request.args.get('next') or url_for('dashboard')
                return redirect(next_url)
            else:
                flash('Invalid password', 'error')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.route('/')
    def dashboard():
        # सीधे login पेज पर रीडायरेक्ट
        return redirect(url_for('login'))

    @app.route('/topics')
    @login_required
    def topics():
        category = request.args.get('category')
        page = int(request.args.get('page', 1))
        per_page = 20

        posts = topic_selector.get_published_history(limit=1000, category=category)

        # Pagination
        total = len(posts)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_posts = posts[start:end]

        return render_template('topics.html',
                             posts=paginated_posts,
                             categories=VEHICLE_CATEGORIES,
                             current_category=category,
                             page=page,
                             total_pages=(total + per_page - 1) // per_page,
                             total=total)

    @app.route('/categories')
    @login_required
    def categories():
        stats = topic_selector.get_stats()
        cat_stats = stats.get('by_category', {})

        category_list = []
        for key, info in VEHICLE_CATEGORIES.items():
            category_list.append({
                'key': key,
                'name': info['name'],
                'description': info['description'],
                'examples': info['examples'][:3],
                'post_count': cat_stats.get(key, 0),
                'hashtags': info['hashtags'][:5]
            })

        return render_template('categories.html', categories=category_list)

    @app.route('/scheduler')
    @login_required
    def scheduler_view():
        jobs = scheduler.get_pending_jobs()
        history = scheduler.get_recent_history(50)
        stats = scheduler.get_stats()

        return render_template('scheduler.html',
                             pending_jobs=jobs,
                             history=history,
                             stats=stats,
                             config=scheduler.config.automation)

    @app.route('/generate', methods=['GET', 'POST'])
    @login_required
    def generate():
        if request.method == 'POST':
            category = request.form.get('category')
            vehicle_name = request.form.get('vehicle_name')
            vehicle_year = int(request.form.get('vehicle_year', datetime.now().year))
            style = request.form.get('style', 'Aesthetic Handwritten Illustrated Infographic')
            post_now = request.form.get('post_now') == 'on'

            # Create topic
            from src.topic_selector import Topic
            topic = Topic(
                category_key=category,
                vehicle_name=vehicle_name,
                vehicle_year=vehicle_year
            )

            try:
                # Research
                researcher = get_researcher()
                specs = researcher.research(topic)

                # Generate
                result = content_generator.generate(topic, specs, style)

                flash(f'Generated: {result.image_path}', 'success')

                if post_now:
                    caption, hashtags = content_generator.generate_caption(topic, specs)
                    post_result = instagram_poster.post_image(result.image_path, caption)

                    if post_result.status == 'published':
                        topic_selector.mark_published(
                            topic, result.image_path, post_result.instagram_post_id,
                            caption, hashtags
                        )
                        flash(f'Posted to Instagram: {post_result.instagram_post_id}', 'success')
                    else:
                        flash(f'Post failed: {post_result.error_message}', 'error')

                return redirect(url_for('generate'))

            except Exception as e:
                logger.error(f"Generation failed: {e}", exc_info=True)
                flash(f'Generation failed: {str(e)}', 'error')

        styles = content_generator.config.image.styles
        return render_template('generate.html',
                             categories=VEHICLE_CATEGORIES,
                             styles=styles)

    @app.route('/settings')
    @login_required
    def settings():
        config = get_config()
        return render_template('settings.html', config=config)

    # API Routes
    @app.route('/api/stats')
    @login_required
    def api_stats():
        stats = topic_selector.get_stats()
        scheduler_stats = scheduler.get_stats()
        return jsonify({
            'topics': stats,
            'scheduler': scheduler_stats,
            'timestamp': datetime.now().isoformat()
        })

    @app.route('/api/post-now', methods=['POST'])
    @login_required
    def api_post_now():
        category = request.json.get('category') if request.json else None
        job = scheduler.post_now(category)
        return jsonify({
            'job_id': job.id,
            'status': job.status.value
        })

    @app.route('/api/job/<job_id>')
    @login_required
    def api_job_status(job_id):
        job = scheduler.get_job_status(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404

        return jsonify({
            'id': job.id,
            'status': job.status.value,
            'topic': job.topic.__dict__ if job.topic else None,
            'scheduled_time': job.scheduled_time.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'error': job.error,
            'image_path': job.image_result.image_path if job.image_result else None,
            'post_id': job.post_result.instagram_post_id if job.post_result else None
        })

    @app.route('/api/reschedule', methods=['POST'])
    @login_required
    def api_reschedule():
        scheduler.reschedule()
        return jsonify({'success': True})

    @app.route('/api/test-instagram')
    @login_required
    def api_test_instagram():
        try:
            if instagram_poster.verify_token():
                account = instagram_poster.get_account_info()
                return jsonify({
                    'success': True,
                    'username': account.username,
                    'followers': account.followers_count,
                    'account_type': account.account_type
                })
            else:
                return jsonify({'success': False, 'error': 'Token verification failed'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @app.route('/api/generate', methods=['POST'])
    @login_required
    def api_generate():
        data = request.json
        category = data.get('category')
        vehicle_name = data.get('vehicle_name')
        vehicle_year = data.get('vehicle_year', datetime.now().year)
        style = data.get('style')

        from src.topic_selector import Topic
        topic = Topic(category_key=category, vehicle_name=vehicle_name, vehicle_year=vehicle_year)

        researcher = get_researcher()
        specs = researcher.research(topic)

        result = content_generator.generate(topic, specs, style)

        return jsonify({
            'success': True,
            'image_path': result.image_path,
            'style': result.style_used,
            'generation_time': result.generation_time
        })

    @app.route('/api/settings', methods=['GET', 'POST'])
    @login_required
    def api_settings():
        if request.method == 'GET':
            config = get_config()
            # Return current config as dict
            return jsonify({
                'instagram': {
                    'access_token': config.instagram.access_token,
                    'user_id': config.instagram.user_id,
                    'app_id': config.instagram.app_id,
                    'app_secret': config.instagram.app_secret
                },
                'image': {
                    'width': config.image.width,
                    'height': config.image.height,
                    'default_style': config.image.default_style,
                    'styles': config.image.styles
                },
                'research': {
                    'timeout': config.research.timeout,
                    'max_retries': config.research.max_retries,
                    'cache_ttl': config.research.cache_ttl,
                    'sources': config.research.sources
                },
                'automation': {
                    'timezone': config.automation.timezone,
                    'daily_limit': config.automation.daily_limit,
                    'post_times': config.automation.post_times,
                    'enabled': config.automation.enabled,
                    'randomize_category': config.automation.randomize_category,
                    'randomize_style': config.automation.randomize_style,
                    'skip_posted': config.automation.skip_posted
                },
                'admin': {
                    'host': config.admin.host,
                    'port': config.admin.port,
                    'secret_key': config.admin.secret_key
                },
                'logging': {
                    'level': config.logging.level,
                    'file': config.logging.file
                }
            })

        # POST - save settings
        data = request.json
        section = data.get('section')

        try:
            # Load current config.local.yaml
            config_path = Path('config.local.yaml')
            if config_path.exists():
                with open(config_path, 'r') as f:
                    local_config = yaml.safe_load(f) or {}
            else:
                local_config = {}

            # Update the section
            if section == 'instagram':
                local_config.setdefault('instagram', {})
                local_config['instagram'].update({
                    'access_token': data.get('access_token'),
                    'user_id': data.get('user_id'),
                    'app_id': data.get('app_id'),
                    'app_secret': data.get('app_secret')
                })
            elif section == 'image':
                local_config.setdefault('image', {})
                local_config['image'].update({
                    'width': data.get('width'),
                    'height': data.get('height'),
                    'default_style': data.get('default_style')
                })
            elif section == 'research':
                local_config.setdefault('research', {})
                local_config['research'].update({
                    'timeout': data.get('timeout'),
                    'max_retries': data.get('max_retries'),
                    'cache_ttl': data.get('cache_ttl'),
                    'sources': data.get('sources')
                })
            elif section == 'automation':
                local_config.setdefault('automation', {})
                local_config['automation'].update({
                    'timezone': data.get('timezone'),
                    'daily_limit': data.get('daily_limit'),
                    'post_times': data.get('post_times'),
                    'enabled': data.get('enabled'),
                    'randomize_category': data.get('randomize_category'),
                    'randomize_style': data.get('randomize_style'),
                    'skip_posted': data.get('skip_posted')
                })
            elif section == 'admin':
                local_config.setdefault('admin', {})
                local_config['admin'].update({
                    'host': data.get('host'),
                    'port': data.get('port'),
                    'secret_key': data.get('secret_key')
                })
            elif section == 'logging':
                local_config.setdefault('logging', {})
                local_config['logging'].update({
                    'level': data.get('level'),
                    'file': data.get('file')
                })
            else:
                return jsonify({'success': False, 'error': 'Invalid section'}), 400

            # Save to config.local.yaml
            with open(config_path, 'w') as f:
                yaml.dump(local_config, f, default_flow_style=False, sort_keys=False)

            # Reload config
            reload_config()

            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Failed to save settings: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/reload-config', methods=['POST'])
    @login_required
    def api_reload_config():
        try:
            reload_config()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/topic/<topic_id>', methods=['DELETE'])
    @login_required
    def api_delete_topic(topic_id):
        try:
            topic_selector.delete_topic(topic_id)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/job/<job_id>/run', methods=['POST'])
    @login_required
    def api_run_job(job_id):
        try:
            job = scheduler.get_job_status(job_id)
            if not job:
                return jsonify({'success': False, 'error': 'Job not found'}), 404

            # Execute the job
            scheduler._execute_job(job_id)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/job/<job_id>/cancel', methods=['POST'])
    @login_required
    def api_cancel_job(job_id):
        try:
            scheduler.cancel_job(job_id)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # SocketIO events
    @socketio.on('connect')
    def handle_connect():
        if session.get('logged_in'):
            emit('connected', {'status': 'connected'})
            # Send initial stats
            stats = topic_selector.get_stats()
            scheduler_stats = scheduler.get_stats()
            emit('stats_update', {
                'topics': stats,
                'scheduler': scheduler_stats
            })

    @socketio.on('request_stats')
    def handle_request_stats():
        stats = topic_selector.get_stats()
        scheduler_stats = scheduler.get_stats()
        emit('stats_update', {
            'topics': stats,
            'scheduler': scheduler_stats
        })

    # Background task to emit updates
    def background_stats_emitter():
        while True:
            socketio.sleep(30)
            if socketio.server.manager.rooms:
                stats = topic_selector.get_stats()
                scheduler_stats = scheduler.get_stats()
                socketio.emit('stats_update', {
                    'topics': stats,
                    'scheduler': scheduler_stats
                }, namespace='/')

    # Start background task
    socketio.start_background_task(background_stats_emitter)

    return app, socketio


def run_admin_panel(host: str = "0.0.0.0", port: int = 8080, debug: bool = False):
    """Run the admin panel."""
    config = get_config()

    # Setup logging
    setup_logging(config.logging.level, config.logging.file)

    app, socketio = create_app()

    logger.info(f"Starting admin panel on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    run_admin_panel()