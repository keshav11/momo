import os

from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    send_from_directory,
)
from flask_bootstrap import Bootstrap
from momo.plugins.flask import filters, functions
from momo.plugins.flask.utils import get_public_functions
from momo.plugins.flask.sorting import sort_nodes_by_request


FLASK_DEFAULT_HOST = '127.0.0.1'
FLASK_DEFAULT_PORT = 7000
FLASK_DEFAULT_DEBUG = True
FLASK_APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
FLASK_TEMPLATE_FOLDER = os.path.join(FLASK_APP_ROOT, 'templates')
FLASK_STATIC_FOLDER = os.path.join(FLASK_APP_ROOT, 'static')

app = Flask(
    import_name=__name__,
    template_folder=FLASK_TEMPLATE_FOLDER,
    static_folder=FLASK_STATIC_FOLDER,
)

# instrument app
Bootstrap(app)

# extensions
app.jinja_env.add_extension('jinja2.ext.do')

# register default filters
app.jinja_env.filters.update(get_public_functions(filters))

# register default global functions
app.jinja_env.globals.update(get_public_functions(functions))

app.url_map.strict_slashes = False

"""
Query strings for all views:

    ?sort=: sort by a key, which can be prefixed with a: (attr), n: (node
    object attribute), and f: (a pre-defined function). For example:

        ?sort=n.name means to sort by node name.
        ?sort=a.size means to sort by attr name "size".
        ?sort=f.rank means to sort using a sorting key function: sort_by_rank.

    ?desc=: in descending order (only effective when ?sort= is present)

    ?view=: view method for nodes, which can be "list" (default) and "table".

"""


@app.route('/node')
@app.route('/node/<path:path>')
def node(path=None):
    if path is None:
        return redirect('/')

    root = app.config['MOMO_ROOT_NODE']
    funcs = app.config['MOMO_NODES_FUNCTIONS']
    g.sorting_functions = app.config['MOMO_SORTING_FUNCTIONS']

    g.path = path
    g.title = os.path.basename(path)
    g.view = (
        request.args.get('view') or
        app.config['MOMO_VIEW_NODE'] or
        app.config['MOMO_VIEW']
    )

    funcs['pre_node'](
        path=path,
        root=root,
        request=request
    )

    node = funcs['process_node'](
        path=path,
        root=root,
        request=request,
    )

    g.nodes = node.node_vals

    # apply default sorting
    g.nodes = app.config['MOMO_NODES_SORTING'](g.nodes)
    # sort nodes by request args
    g.nodes = sort_nodes_by_request(g.nodes, request, g)

    node = funcs['post_node'](
        path=path,
        root=root,
        request=request,
        node=node,
    )

    return render_template('node.html', node=node)


@app.route('/search')
@app.route('/search/<path:term>')
def search(term=None):
    """
    A search term is a path-like string. See parse_search_term for usage.

    Query string is "?q=", which indicates a query that is used to match
    content of all attrs of all nodes all filtered in the above steps.
    """

    root = app.config['MOMO_ROOT_NODE']
    funcs = app.config['MOMO_NODES_FUNCTIONS']
    g.sorting_functions = app.config['MOMO_SORTING_FUNCTIONS']

    g.title = 'Search'
    g.view = (
        request.args.get('view') or
        app.config['MOMO_VIEW_SEARCH'] or
        app.config['MOMO_VIEW']
    )

    funcs['pre_search'](
        root=root,
        term=term,
        request=request,
    )

    nodes = funcs['process_search'](
        root=root,
        term=term,
        request=request,
    )

    # apply default sorting
    nodes = app.config['MOMO_NODES_SORTING'](nodes)
    # sort nodes by request args
    nodes = sort_nodes_by_request(nodes, request, g)

    nodes = funcs['post_search'](
        root=root,
        term=term,
        request=request,
        nodes=nodes,
    )

    return render_template('search.html', nodes=nodes)


@app.route('/')
def index():
    """
    Default index page that lists all nodes of root, deemed as a special
    case for /node/.
    """

    root = app.config['MOMO_ROOT_NODE']
    funcs = app.config['MOMO_NODES_FUNCTIONS']
    g.sorting_functions = app.config['MOMO_SORTING_FUNCTIONS']

    g.title = 'Index'
    g.view = (
        request.args.get('view') or
        app.config['MOMO_VIEW_INDEX'] or
        app.config['MOMO_VIEW']
    )

    funcs['pre_index'](
        root=root,
        request=request,
    )

    nodes = funcs['process_index'](
        root=root,
        request=request,
    )

    # apply default sorting
    nodes = app.config['MOMO_NODES_SORTING'](nodes)
    # sort nodes by request args
    nodes = sort_nodes_by_request(nodes, request, g)

    nodes = funcs['post_index'](
        root=root,
        request=request,
        nodes=nodes,
    )

    return render_template('index.html', nodes=nodes)


@app.route('/files/<path:filename>')
def files(filename):
    """Get user files."""
    return send_from_directory(app.config['MOMO_FILES_FOLDER'], filename)


@app.before_request
def fix_trailing():
    """Always add a single trailing slash."""
    rp = request.path
    # get query string
    parts = request.full_path.rsplit('?', 1)
    qs = ''
    if len(parts) > 1:
        qs = '?' + parts[-1]
    if rp != '/':
        if not rp.endswith('/'):
            return redirect(rp + '/' + qs)
        elif rp.endswith('//'):
            return redirect(rp.rstrip('/') + '/' + qs)
