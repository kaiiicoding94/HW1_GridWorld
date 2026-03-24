from flask import Flask, render_template, request, jsonify
import random
import copy

app = Flask(__name__)

# ─── Constants ───────────────────────────────────────────────────────
GAMMA = 0.9          # discount factor
THETA = 1e-6         # convergence threshold
STEP_REWARD = -1     # reward for each step
GOAL_REWARD = 0      # reward at goal (terminal)

ACTIONS = ['up', 'down', 'left', 'right']
DELTAS = {
    'up':    (-1, 0),
    'down':  (1, 0),
    'left':  (0, -1),
    'right': (0, 1),
}


def _next_state(r, c, action, n, obstacles):
    """Return next (row, col) after taking action from (r, c)."""
    dr, dc = DELTAS[action]
    nr, nc = r + dr, c + dc
    if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in obstacles:
        return nr, nc
    return r, c  # stay in place if hitting wall or obstacle


# ─── Routes ──────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/random_policy', methods=['POST'])
def random_policy():
    """Generate a random policy for each free cell."""
    data = request.get_json()
    n = data['n']
    start = tuple(data['start'])
    end = tuple(data['end'])
    obstacles = set(tuple(o) for o in data['obstacles'])

    policy = {}
    for r in range(n):
        for c in range(n):
            if (r, c) == end or (r, c) in obstacles:
                continue
            policy[f"{r},{c}"] = random.choice(ACTIONS)

    return jsonify({'policy': policy})


@app.route('/api/policy_evaluation', methods=['POST'])
def policy_evaluation():
    """Run iterative policy evaluation on the supplied policy."""
    data = request.get_json()
    n = data['n']
    start = tuple(data['start'])
    end = tuple(data['end'])
    obstacles = set(tuple(o) for o in data['obstacles'])
    policy = data['policy']  # dict  "r,c" -> action

    # Initialise V(s) = 0 for all states
    V = {}
    for r in range(n):
        for c in range(n):
            if (r, c) in obstacles:
                continue
            V[f"{r},{c}"] = 0.0

    # Iterative policy evaluation
    for _ in range(10000):
        delta = 0.0
        for r in range(n):
            for c in range(n):
                key = f"{r},{c}"
                if (r, c) in obstacles or (r, c) == end:
                    continue
                action = policy.get(key)
                if action is None:
                    continue
                nr, nc = _next_state(r, c, action, n, obstacles)
                nkey = f"{nr},{nc}"
                reward = GOAL_REWARD if (nr, nc) == end else STEP_REWARD
                new_v = reward + GAMMA * V.get(nkey, 0.0)
                delta = max(delta, abs(new_v - V[key]))
                V[key] = new_v
        if delta < THETA:
            break

    # Round for display
    V_rounded = {k: round(v, 2) for k, v in V.items()}
    return jsonify({'values': V_rounded})


@app.route('/api/value_iteration', methods=['POST'])
def value_iteration():
    """Run value iteration; return optimal policy + V(s)."""
    data = request.get_json()
    n = data['n']
    start = tuple(data['start'])
    end = tuple(data['end'])
    obstacles = set(tuple(o) for o in data['obstacles'])

    # Initialise V(s)
    V = {}
    for r in range(n):
        for c in range(n):
            if (r, c) in obstacles:
                continue
            V[f"{r},{c}"] = 0.0

    # Value iteration
    for _ in range(10000):
        delta = 0.0
        for r in range(n):
            for c in range(n):
                key = f"{r},{c}"
                if (r, c) in obstacles or (r, c) == end:
                    continue
                old_v = V[key]
                best_v = float('-inf')
                for action in ACTIONS:
                    nr, nc = _next_state(r, c, action, n, obstacles)
                    nkey = f"{nr},{nc}"
                    reward = GOAL_REWARD if (nr, nc) == end else STEP_REWARD
                    v = reward + GAMMA * V.get(nkey, 0.0)
                    if v > best_v:
                        best_v = v
                V[key] = best_v
                delta = max(delta, abs(best_v - old_v))
        if delta < THETA:
            break

    # Extract greedy policy
    policy = {}
    for r in range(n):
        for c in range(n):
            key = f"{r},{c}"
            if (r, c) in obstacles or (r, c) == end:
                continue
            best_action = None
            best_v = float('-inf')
            for action in ACTIONS:
                nr, nc = _next_state(r, c, action, n, obstacles)
                nkey = f"{nr},{nc}"
                reward = GOAL_REWARD if (nr, nc) == end else STEP_REWARD
                v = reward + GAMMA * V.get(nkey, 0.0)
                if v > best_v:
                    best_v = v
                    best_action = action
            policy[key] = best_action

    V_rounded = {k: round(v, 2) for k, v in V.items()}
    return jsonify({'policy': policy, 'values': V_rounded})


if __name__ == '__main__':
    app.run(debug=True)
