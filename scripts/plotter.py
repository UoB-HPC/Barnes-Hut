import argparse
import math

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description="Create animation from nbody output.")
    subparsers = parser.add_subparsers(dest='command')

    parser_pos = subparsers.add_parser('pos', help='Animate positions')
    sim_group = parser_pos.add_mutually_exclusive_group(required=True)
    sim_group.add_argument('--galaxy', action='store_true', help="Select galaxy animation.")
    sim_group.add_argument('--general', action='store_true', help="Try animate position file.")

    file_group = parser_pos.add_mutually_exclusive_group(required=True)
    file_group.add_argument('--mp4', action='store_true', help="Save as mp4 file.")
    file_group.add_argument('--gif', action='store_true', help="Save as gif file.")

    parser_energy = subparsers.add_parser('energy', help='Plot energy')

    return parser.parse_args()


def save_animation(ani, mp4=False):
    file_name = 'nbody_animation'

    print(f'Saving animation to {file_name} ...')

    fps= 1000 / ani.event_source.interval
    metadata = dict(title='n-body simulation', comment='Made with stdpar')

    if mp4:
        writer = animation.FFMpegWriter(
            fps=fps,
            metadata=metadata,
        )
        file_name += '.mp4'
    else:
        # gif writer
        writer = animation.PillowWriter(
            fps=fps,
            metadata=metadata,
        )
        file_name += '.gif'

    ani.save(
        file_name,
        writer=writer,
        savefig_kwargs={'pad_inches': 0},
    )


def read_points(file_name='positions.bin'):
    print(f'Reading {file_name}...')
    # read properties of file
    file_info = np.memmap(file_name, np.uint32, 'r', shape=4)

    # extract properties
    sim_size, steps, data_size, dim = file_info
    dtype = np.float32 if data_size == 4 else np.float64 if data_size == 8 else 1 / 0

    # load data
    data = np.memmap(file_name, dtype, 'r', shape=(steps, sim_size, dim), offset=4 * len(file_info))
    data = np.transpose(data, (0, 2, 1))

    print(f'Loaded {data.shape}')

    return data


def read_energy(file_name='energy.bin'):
    print(f'Reading {file_name}...')
    # read properties of file
    file_info = np.memmap(file_name, np.uint32, 'r', shape=2)

    # extract properties
    steps, data_size = file_info
    dtype = np.float32 if data_size == 4 else np.float64 if data_size == 8 else 1 / 0

    # load data
    data = np.memmap(file_name, dtype, 'r', shape=(steps, 2), offset=8)
    data = np.swapaxes(data, 0, 1)

    print(f'Loaded {data.shape}')

    return data


def animate_galaxy():
    data = read_points()
    d3 = data.shape[1] == 3

    # set up background
    size = 500
    fig = plt.figure(figsize=(6, 6))
    if d3:
        size /= 3
        ax = fig.add_subplot(projection='3d')
        ax.set_zlim([-size, size])
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_zticklabels([])
    else:
        ax = fig.add_subplot()
        ax.set_axis_off()
        fig.tight_layout()
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_xlim([-size, size])
    ax.set_ylim([-size, size])

    # create each frame
    artists = []
    for step in data[::10, ...]:
        n = step.shape[-1]
        step_1, step_2 = step[:, :n // 2], step[:, n // 2:]

        bh1, step_1 = step_1[:, 0], step_1[:, 1:]
        bh2, step_2 = step_2[:, 0], step_2[:, 1:]

        artist1 = ax.scatter(*step_1, marker='o', animated=True, color='red', s=1)
        artist2 = ax.scatter(*step_2, marker='o', animated=True, color='blue', s=1)
        artist3 = ax.scatter(*bh1, animated=True, color='red')
        artist4 = ax.scatter(*bh2, animated=True, color='blue')

        artists.append([artist1, artist2, artist3, artist4])

    print(f'There are {len(artists)} frames')

    # build animation
    ani = animation.ArtistAnimation(fig=fig, artists=artists, interval=100, blit=True, repeat_delay=1000)
    print('Animation created!')

    return ani


def animate_general():
    data = read_points()
    d3 = data.shape[1] == 3
    if data.shape[1] not in [2, 3]:
        raise ValueError("Can only support 2 or 3 dimensions in general plot")

    # find boundary values in all directions
    boundary_max = data.max(axis=0).max(axis=1)
    boundary_min = data.min(axis=0).min(axis=1)

    # set up background
    fig = plt.figure(figsize=(6, 6))
    if d3:
        ax = fig.add_subplot(projection='3d')
        ax.set_zlim([boundary_min[2], boundary_max[2]])
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_zticklabels([])
    else:
        ax = fig.add_subplot()
        ax.set_axis_off()
        fig.tight_layout()
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_xlim([boundary_min[0], boundary_max[0]])
    ax.set_ylim([boundary_min[1], boundary_max[1]])

    # create each frame
    artists = []
    for step in data:
        artist1 = ax.scatter(*step, marker='o', animated=True, s=1, color='blue')

        artists.append([artist1])

    print(f'There are {len(artists)} frames')

    # build animation
    ani = animation.ArtistAnimation(fig=fig, artists=artists, interval=100, blit=True, repeat_delay=1000)
    print('Animation created!')

    return ani



def plot_energy():
    energy_values = read_energy()

    plt.plot(energy_values[0, ...], label='Kinetic')
    plt.plot(energy_values[1, ...], label='Gravitational')
    plt.plot(energy_values[0, ...] + energy_values[1, ...], label='Total')

    plt.xlabel('Timestep')
    plt.ylabel('Energy')
    plt.title('Energy by Time in n-body simulation')
    plt.legend()
    plt.grid(True)
    plt.show()


def main(args):
    if args.command == 'pos':
        if args.galaxy:
            ani = animate_galaxy()
        elif args.general:
            ani = animate_general()
        else:
            raise ValueError('Unknown option')
        save_animation(ani, mp4=args.mp4)
    elif args.command == 'energy':
        plot_energy()
    else:
        print('No plot selected')


if __name__ == '__main__':
    main(parse_args())
