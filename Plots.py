import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from Constants import *
import os

user_scatter = []
agent_scatter = []
patch_grid = [[]]

# array of color used in comparison graphics
colors = [
    #'red'
    'darkorange'
    , 'limegreen'
    #, 'cornflowerblue'
    #, 'mediumorchid'
          ]

def plot_area(area, users, base_stations, agents, type_of_search, num_of_iter, prob_matrix_history, expl_weight, use_expl, use_bs, use_custom_prob, show_plot=False):
    fig, ax = plt.subplots()
    plt.axis('square')
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.8)
    plt.xlim(0, area.width)
    plt.ylim(0, area.length)

    # define plot legend
    users_label = Line2D([0], [0], marker='x', color='red', label='Utenti non coperti', markerfacecolor='red',
                         markersize=6, linestyle='None')
    covered_users_label = Line2D([0], [0], marker='^', color='green', label='Utenti coperti', markerfacecolor='green',
                                 markersize=6, linestyle='None')
    base_stations_label = Line2D([0], [0], marker='o', color='blue', label='Base stations', markerfacecolor='blue',
                                 markersize=6, linestyle='None')
    agents_label = Line2D([0], [0], marker='o', color='black', label='Agenti', markerfacecolor='black',
                          markersize=6, linestyle='None')
    plt.legend(handles=[users_label, covered_users_label, base_stations_label, agents_label], bbox_to_anchor=(0.7, 1.3),
               loc='upper right')

    # extract and display first elements
    users_x, users_y = zip(*[user.get_position() for user in users])

    if use_bs:
        base_stations_x, base_stations_y = zip(*[base_station.get_2D_position() for base_station in base_stations])
        plt.scatter(base_stations_x, base_stations_y, color='blue', zorder=2)

    trajectories = [agent.trajectory for agent in agents]
    lines = [ax.plot([], [], lw=0.7)[0] for _ in trajectories]
    # [0] allow to work directly with Line2D objects, not with list of lines

    def init():
        for line in lines:
            line.set_data([], [])
        return lines

    def init_prob():
        for line in lines:
            line.set_data([], [])

        global patch_grid
        # first index is for x-axis, second index for y-axis
        if use_expl:
            matrix = prob_matrix_history[0]
            patch_grid = [[Rectangle((j * EXPLORATION_CELL_WIDTH, k * EXPLORATION_CELL_HEIGTH),
                                 EXPLORATION_CELL_WIDTH, EXPLORATION_CELL_HEIGTH,
                                facecolor="#ff9900", edgecolor='#ff8000', alpha=0, zorder=1)
                       for k in range(matrix.shape[1])]
                      for j in range(matrix.shape[0])]

            for j in range(matrix.shape[0]):
                for k in range(matrix.shape[1]):
                    ax.add_patch(patch_grid[j][k])

            for i in range(20):
                ax.add_patch(Rectangle((1050, 1000-41*(i+1)), 40, 40, facecolor="#ff9900", edgecolor='#ff8000', alpha=i*0.05, zorder=1, clip_on=False))
                plt.text(1100, 1000-41*(i+1),f"prob. {round(i*0.05, 2)}", size='x-small', fontfamily='monospace')
            ax.add_patch(Rectangle((1050, 1000-41), 40, 40, facecolor="#ffffff", edgecolor='#ff8000', alpha=0.1, zorder=1, clip_on=False))

        return lines

    def animate(i):
        # this two ifs are used to clear the plot from the precedent frame (slicing avoid smudges in animation)
        global user_scatter
        for scatter in user_scatter[:]:
            scatter.remove()
            user_scatter.remove(scatter)

        global agent_scatter
        for scatter in agent_scatter[:]:
            scatter.remove()
            agent_scatter.remove(scatter)

        colors = ['green' if user.coverage_history[i] else 'red' for user in users]
        markers = ['^' if user.coverage_history[i] else 'x' for user in users]

        # draw users' markers
        for xu, yu, color2, marker in zip(users_x, users_y, colors, markers):
            user_scatter.append(plt.scatter(xu, yu, color=color2, marker=marker, zorder=2))

        # draw users' trajectory
        for agent, trajectory in zip(agents, trajectories):
            xa, ya = trajectory[i]
            agent_scatter.append(plt.scatter(xa, ya, color='black', zorder=2))

        # used for the final coverage image
        if i == 0 and not use_expl:
            plt.savefig(f'Simulations output/custom prob {use_custom_prob}/{num_of_iter}/initial coverage.png')

        if i == len(trajectories[0]) - 1 and not use_expl:
            for line, trajectory in zip(lines, trajectories):
                x_coord = [coord[0] for coord in trajectory[:i + 1]]
                y_coord = [coord[1] for coord in trajectory[:i + 1]]
                line.set_data(x_coord, y_coord)
            plt.savefig(f'Simulations output/custom prob {use_custom_prob}/{num_of_iter}/final coverage.png')

        return lines

    def animate_prob(i):

        if use_expl:
            matrix = prob_matrix_history[i]
            global patch_grid
            for j in range(matrix.shape[0]):
                for k in range(matrix.shape[1]):
                    patch_grid[j][k].set_alpha(matrix[j][k])

        animate(i)
        # used for the final coverage image
        if i == 0:
            plt.savefig(f'Simulations output/custom prob {use_custom_prob}/{num_of_iter}/initial coverage.png')

        if i == len(trajectories[0]) -1:
            for line, trajectory in zip(lines, trajectories):
                x_coord = [coord[0] for coord in trajectory[:i + 1]]
                y_coord = [coord[1] for coord in trajectory[:i + 1]]
                line.set_data(x_coord, y_coord)
            plt.savefig(f'Simulations output/custom prob {use_custom_prob}/{num_of_iter}/final coverage.png')

        # USE FOR DEBUG
        #os.makedirs(os.path.dirname(f'Simulations output/{type_of_search} search/{expl_weight} weight/expl {use_expl}/BS {use_bs}/{num_of_iter}/animation frames/'), exist_ok=True)
        #plt.savefig(f'Simulations output/{type_of_search} search/{expl_weight} weight/expl {use_expl}/BS {use_bs}/{num_of_iter}/animation frames/frame_{i}.png')

        return lines

    ani = animation.FuncAnimation(fig, animate, init_func=init, frames=len(trajectories[0]), interval=200, blit=True)
    os.makedirs(os.path.dirname(f'Simulations output/custom prob {use_custom_prob}/{num_of_iter}'), exist_ok=True)
    ani.save(f'Simulations output/custom prob {use_custom_prob}/{num_of_iter}/animation.mp4', writer='ffmpeg')

    if use_expl:
        ani_prob = animation.FuncAnimation(fig, animate_prob, init_func=init_prob, frames=len(trajectories[0]), interval=200, blit=True)
        ani_prob.save(f'Simulations output/custom prob {use_custom_prob}/{num_of_iter}/animation_prob.mp4', writer='ffmpeg')

    if show_plot:
        plt.show()
    plt.close()


def plot_coverage(coverages, time_elapsed, type_of_search, expl_weight, num_of_iter, use_expl, use_bs, use_custom_prob, show_plot=False):
    plt.subplots()
    plt.plot(range(len(coverages)), coverages)
    plt.xlabel('Iterations')
    plt.ylabel(f'Coverage ({type_of_search})')
    plt.text(1.1, 1.1, f'Time elapsed: {time_elapsed}', horizontalalignment='right', verticalalignment='top',
             transform=plt.gca().transAxes)
    os.makedirs(os.path.dirname(f'Simulations output/custom prob {use_custom_prob}/{num_of_iter}/'), exist_ok=True)
    plt.savefig(f'Simulations output/custom prob {use_custom_prob}/{num_of_iter}/coverage_graphic.png')
    if show_plot:
        plt.show()
    plt.close()


def plot_exploration(exploration_levels, time_elapsed, type_of_search, expl_weight, num_of_iter, use_bs, use_custom_prob, show_plot=False):
    plt.subplots()
    plt.plot(range(len(exploration_levels)), exploration_levels)
    plt.xlabel('Iterations')
    plt.ylabel(f'Exploration ({type_of_search})')
    plt.text(1.1, 1.1, f'Time elapsed: {time_elapsed}', horizontalalignment='right', verticalalignment='top',
             transform=plt.gca().transAxes)
    os.makedirs(os.path.dirname(f'Simulations output/custom prob {use_custom_prob}/{num_of_iter}/'), exist_ok=True)
    plt.savefig(f'Simulations output/custom prob {use_custom_prob}/{num_of_iter}/exploration_graphic.png')
    if show_plot:
        plt.show()
    plt.close()


def plot_coverages_comparison(coverages, legend, show_plot=False, path=None):
    plt.subplots()
    j = 0 # index to iter through colors
    for coverage in coverages:
        plt.plot(range(len(coverage)), coverage, color=colors[j], label=legend[j], linewidth=2)
        j += 1
    plt.legend()
    plt.xlabel('Iterations')
    plt.ylabel('Coverage')
    if path is None:
        plt.savefig(f'coverages_graphic_comparison.png', bbox_inches='tight')
    else:
        plt.savefig(f'{path}/coverages_graphic_comparison.png', bbox_inches='tight')
    if show_plot:
        plt.show()
    plt.close()

def plot_exploration_comparison(expl_levels, legend, show_plot=False, path=None):
    plt.subplots()
    j = 0 # index to iter through colors
    for expl in expl_levels:
        plt.plot(range(len(expl)), expl, color=colors[j], label=legend[j], linewidth=2)
        j += 1
    plt.legend()
    plt.xlabel('Iterations')
    plt.ylabel('Exploration')
    if path is None:
        plt.savefig(f'exploration_graphic_comparison.png', bbox_inches='tight')
    else:
        plt.savefig(f'{path}/exploration_graphic_comparison.png', bbox_inches='tight')
    if show_plot:
        plt.show()
    plt.close()