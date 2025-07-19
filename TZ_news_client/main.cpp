#include <QApplication>
#include "NewsClient.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    NewsClient client;
    client.show();
    return app.exec();
}
