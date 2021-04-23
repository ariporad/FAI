from env import FlappyEnv
import numpy as np
import tensorflow as tf
import pickle
import pandas as pd


def execute_checkpoint(model, q_examples, use_pipes, episode, log, buffer_length, config):
    all_rewards = []
    all_q_vals = []
    all_steps = []
    best_steps = float('-inf')
    best_reward = float('-inf')
    new_best_found = False
    for example in q_examples:
        example = np.array(example).reshape((1, 50, 50, 4))
        q_vals = model(example, training=False)[0].numpy()
        action = tf.argmax(q_vals).numpy()
        all_q_vals.append(q_vals[action])

    for _ in range(config['train'].getint('eval_episodes')):
        env = FlappyEnv(use_pipes=use_pipes)
        s = env.reset()
        ep_states = [s[-1]]
        s = np.array(s).reshape((1, 50, 50, 4))
        step = 0
        ep_rewards = []
        # ep_q_vals = []
        d = False
        while not d and step < config['train'].getint('max_episode_length'):
            q_vals = model(s, training=False)[0].numpy()
            action = tf.argmax(q_vals).numpy()
            next_s, r, d = env.step(action)
            ep_states.append(next_s[-1])
            next_s = np.array(next_s).reshape((1, 50, 50, 4))
            s = next_s
            ep_rewards.append(r)
            step += 1
        all_steps.append(step)
        all_rewards.append(sum(ep_rewards))

        if step > best_steps:
            best_steps = step
        if sum(ep_rewards) > best_reward:
            best_reward = sum(ep_rewards)
        if len(log['best_reward']) == 0:
            pickle.dump(ep_states, open(config['files']['best_episode_states_path'], 'wb'))
        elif sum(ep_rewards) > max(log['best_reward']):
            new_best_found = True
            pickle.dump(ep_states, open(config['files']['best_episode_states_path'], 'wb'))

    print('---------')
    print('ep:', episode)
    log['episode'].append(episode)
    print('buffer size:', buffer_length)
    print('avg steps', np.mean(all_steps))
    log['avg_steps'].append(np.mean(all_steps))
    print('best steps:', best_steps)
    log['best_steps'].append(best_steps)
    print('avg reward:', np.mean(all_rewards))
    log['avg_reward'].append(np.mean(all_rewards))
    print('best reward:', best_reward)
    log['best_reward'].append(best_reward)
    if new_best_found:
        print('new best trajectory found, saving episode states and weights')
        model.save_weights(config['files']['best_weights_path'])
    print('avg q_vals', np.mean(all_q_vals))
    log['q_vals'].append(np.mean(all_q_vals))

    model.save_weights(config['files']['backup_weights_path'])
    pd.DataFrame(log).to_csv(config['files']['log_path'])
