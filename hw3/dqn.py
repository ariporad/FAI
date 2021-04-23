import pickle
import tensorflow as tf
import numpy as np
from checkpoint import execute_checkpoint
from env import FlappyEnv
from tensorflow import keras


def dqn(start_episode, model, model_target, log, config):
    q_examples = pickle.load(open(config['files']['held_out_states_path'], 'rb'))
    action_history = []
    state_history = []
    state_next_history = []
    rewards_history = []
    done_history = []
    buffer_size = 0
    use_pipes = config['train']['use_pipes'] == 'yes'

    loss_function = keras.losses.Huber()
    optimizer = keras.optimizers.Adam(learning_rate=config['train'].getfloat('learning_rate'), clipnorm=1.0)

    for episode in range(start_episode, config['train'].getint('total_training_episodes')):
        if episode % config['train'].getint('update_target_freq') == 0:
            print('setting target...')
            model_target.set_weights(model.get_weights())

        env = FlappyEnv(use_pipes=use_pipes)
        state = env.reset()
        state = np.array(state).reshape((1, 50, 50, 4))
        ep_reward = 0
        done = False
        step = 0
        while not done and step < config['train'].getint('max_episode_length'):
            step += 1
            # Below, we use the neural network to produce q-values for each action
            # The first q_value corresponds to the 0 action, the second corresponds to the 1 action
            q_values = model(state, training=False)[0].numpy().tolist()

            # Below is the `epsilon` value controlling the rate of random exploration.
            # The default value used by our experiments is 0.05
            epsilon = config['train'].getfloat('epsilon')

            # TODO: IMPORTANT
            # 1. You must implement the epsilon-greedy strategy to encourage exploration.
            #    Use the `q_values` produced by the neural network and the `epsilon` value
            #    taken from the config file above.
            #    The result should assign a value in {0, 1} to the variable `action`
            #    This will not take much coding work
            # 2. Use your environment's `step` method and the action produced by epsilon-greedy
            #    to generate the next state, reward, and done values

            action = None  # You can delete this line when you are finished implementing epsilon-greedy
            next_state, reward, done = None, None, None

            if action is None:
                raise Exception('You must implement the epsilon-greedy strategy')

            if next_state is None or reward is None or done is None:
                raise Exception('You must use your environment to generate the next state.')

            # You do not need to modify the code below!
            # This performs the neural network update by sampling from the buffer of
            # previously encountered states, actions, and rewards.
            # However, you should try to trace through the code to gain a fuller understanding
            # of how the algorithm works.
            next_state = np.array(next_state).reshape((1, 50, 50, 4))
            ep_reward += reward
            action_history.append(action)
            state_history.append(state)
            state_next_history.append(next_state)
            done_history.append(done)
            rewards_history.append(reward)
            buffer_size += 1
            state = next_state

            # If the buffer is full, remove earlier entries so that we are training on more
            # up-to-date data
            if buffer_size > config['train'].getint('max_buffer_size'):
                del rewards_history[:1]
                del state_history[:1]
                del state_next_history[:1]
                del action_history[:1]
                del done_history[:1]
                buffer_size -= 1

            if buffer_size >= config['train'].getint('batch_size') and (step == 1 or
                                                        step % config['train'].getint('update_after_step') == 0):
                # Get indices of samples for replay buffers
                indices = np.random.choice(range(len(done_history)),
                                           size=config['train'].getint('batch_size'))
                # Using list comprehension to sample from replay buffer
                state_sample = np.array([state_history[i] for i in indices])
                state_sample = state_sample.reshape((config['train'].getint('batch_size'), 50, 50, 4))
                state_next_sample = np.array([state_next_history[i] for i in indices])
                state_next_sample = state_next_sample.reshape((config['train'].getint('batch_size'), 50, 50, 4))
                rewards_sample = np.array([rewards_history[i] for i in indices])
                action_sample = np.array([action_history[i] for i in indices])
                done_sample = tf.convert_to_tensor([float(done_history[i]) for i in indices])
                # Build the updated Q-values for the sampled future states
                # Use the target model for stability
                future_rewards = model_target.predict(state_next_sample)
                # Q value = reward + discount factor * expected future reward
                updated_q_values = rewards_sample + config['train'].getfloat('gamma') * tf.reduce_max(future_rewards, axis=1)
                # If final frame set the last value to -1
                updated_q_values = updated_q_values * (1 - done_sample) - done_sample
                # Create a mask so we only calculate loss on the updated Q-values
                masks = tf.one_hot(action_sample, 2)
                with tf.GradientTape() as tape:
                    # Train the model on the states and updated Q-values
                    q_values = model(state_sample, training=True)

                    # Apply the masks to the Q-values to get the Q-value for action taken
                    q_action = tf.reduce_sum(tf.multiply(q_values, masks), axis=1)
                    # Calculate loss between new Q-value and old Q-value
                    loss = loss_function(updated_q_values, q_action)

                # Backpropagation
                grads = tape.gradient(loss, model.trainable_variables)
                optimizer.apply_gradients(zip(grads, model.trainable_variables))

        if episode % config['train'].getint('checkpoint_freq') == 0:
            execute_checkpoint(model, q_examples, use_pipes, episode, log, buffer_size, config)

    print('finished training')
