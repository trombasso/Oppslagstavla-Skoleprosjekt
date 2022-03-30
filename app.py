import pymysql
from flask import Flask, render_template, request, url_for, flash, redirect
import os
from datetime import datetime
from random import randint
import configparser
from faker import Faker

fake = Faker()

app = Flask(__name__)
app.config["SECRET_KEY"] = "MY SUPER SAVE KEY"
path = os.path.dirname(__file__)

config_file = configparser.ConfigParser()
config_file.read(os.path.join(path, "config_local.ini"))  # Use if local
# config_file.read("/var/www/config.ini")  # Use if on server
config_file.sections()

conn = pymysql.connect(
    user=config_file["SETTINGS"]["username"],
    password=config_file["SETTINGS"]["password"],
    host=config_file["DATABASE"]["host"],
    db=config_file["DATABASE"]["db_name"],
    cursorclass=pymysql.cursors.DictCursor,
)


@app.route("/")
def index():
    with conn.cursor() as cur:
        cur = conn.cursor()
        res = cur.execute("SELECT * FROM oppslagstavle")
        tavle = cur.fetchall()

        cur = conn.cursor()
        res_2 = cur.execute("SELECT * FROM kategorier")
        kat = cur.fetchall()

        return render_template("index.html", tavle=tavle, kat=kat)


@app.route("/search=<int:var>")
def search(var):
    with conn.cursor() as cur:
        cur = conn.cursor()
        res = cur.execute("SELECT * FROM oppslagstavle WHERE kategori = %s", [var])
        tavle = cur.fetchall()

        cur = conn.cursor()
        res_2 = cur.execute("SELECT * FROM kategorier")
        kat = cur.fetchall()

        if len(tavle) == 0:
            flash("Sorry, no jobs available for the moment!", "warning")

        return render_template("search.html", tavle=tavle, kat=kat)


@app.route("/item=<int:var>")
def item(var):
    with conn.cursor() as cur:
        cur = conn.cursor()
        cur.execute("UPDATE oppslagstavle SET treff = treff + 1 WHERE id = %s", [var])
        conn.commit()
        cur.close()

        cur = conn.cursor()
        res = cur.execute("SELECT * FROM oppslagstavle WHERE id = %s", [var])
        tavle = cur.fetchall()

        cur = conn.cursor()
        res_2 = cur.execute("SELECT * FROM kategorier")
        kat = cur.fetchall()

        return render_template("item.html", tavle=tavle[0], kat=kat)


@app.route("/delete=<int:var>")
def delete(var):
    cur = conn.cursor()
    cur.execute("DELETE FROM oppslagstavle WHERE id = %s", [var])
    conn.commit()
    cur.close()
    flash("Post deleted!", "warning")
    return redirect(url_for("index"))


@app.route("/innlegg")
def nytt_innlegg():
    return render_template("innlegg.html")


def make_data(n):
    with conn.cursor() as cur:
        cur = conn.cursor()

        cur.execute("INSERT INTO kategorier (navn) VALUES (%s)", ["Ledig Stilling"])
        cur.execute("INSERT INTO kategorier (navn) VALUES (%s)", ["Vikarstilling"])
        cur.execute("INSERT INTO kategorier (navn) VALUES (%s)", ["Sommerjobb"])
        cur.execute("INSERT INTO kategorier (navn) VALUES (%s)", ["Deltidsstilling"])
        cur.execute("INSERT INTO kategorier (navn) VALUES (%s)", ["Stilling Ønskes"])
        conn.commit()

        for _ in range(n):
            kategori = randint(1, 5)
            tittel = fake.job()
            ingress = fake.text(100)
            oppslagstekst = fake.text(400)
            bruker = fake.name()

            cur.execute(
                "INSERT INTO oppslagstavle (kategori, tittel, ingress, oppslagstekst, bruker) VALUES (%s, %s, %s, %s, %s)",
                [kategori, tittel, ingress, oppslagstekst, bruker],
            )

        conn.commit()
        cur.close()


if __name__ == "__main__":
    app.run(debug=True)
