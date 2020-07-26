import logging
from flask import render_template, url_for, request, redirect, Blueprint
from yahtzee.game.utils import roll_dice, get_dice_imgs, get_categories
from yahtzee.game.vars import Game
from yahtzee.game.forms import CategoryForm

log = logging.getLogger(__name__)

game = Blueprint('game', __name__)


@game.route("/game/new")
def new_game():
    global cur_game
    cur_game = Game(1)
    return render_template('new.html', title='New Game', game=cur_game)


@game.route("/game/play", methods=['GET', 'POST'])
def play():
    if 'cur_game' in globals():
        d_imgs = get_dice_imgs(cur_game.dice, cur_game.held) # Dice img string list

        categories = get_categories(cur_game.dice) # List of tuples
        select_categories = [(x, z) for x, y, z in categories] # 2 item tuple
        log.debug(categories)

        form = CategoryForm()
        form.update_categories(cats=select_categories) # Add function to get categories
        if form.validate_on_submit():
            log.debug(form.category.data)

        return render_template('play.html', title='Play', game=cur_game, d_imgs=d_imgs, form=form)
    else:
        print("Could not locate game in global variable list; Redirecting to '/game/new'")
        return redirect(url_for('game.new_game'))


@game.route("/game/roll")
def roll():
    try:
        cur_game.dice = roll_dice(cur_game.dice, cur_game.held)
        cur_game.roll += 1 # Increment roll num

        return redirect(url_for('game.play'))
    except Exception as e:
        print(e)
        print("Could not roll dice; Redirecting to '/game/new'")
        return redirect(url_for('game.new_game'))


@game.route("/game/hold/<int:d>")
def hold(d):
    if d not in cur_game.held and cur_game.dice[d] != 0:
        cur_game.held.append(d)
    elif d in cur_game.held:
        cur_game.held.remove(d)

    return redirect(url_for('game.play'))


# Debug route for testing
@game.route("/game/test", methods=['GET', 'POST'])
def test():
    cats = [('ones', 'Ones - 1'), ('twos', 'Twos - 1'), ('threes', 'Threes - 1')]

    category_form = CategoryForm()
    category_form.update_categories(cats)
    if category_form.validate_on_submit():
        print(f"debug: {category_form.content.data} was submitted.")
        return redirect(url_for('game.test'))

    return render_template('test.html', title='Test', form=category_form)
